# Running NeMo + Parakeet TDT in Docker with Python 3.11

**Context:** Dockerising NVIDIA Parakeet-TDT-0.6B (ASR) using NeMo + FastAPI on an RTX 3060 Ti,
CUDA 12.4, Python 3.11, Ubuntu 22.04.

---

## Problem 1 — torchaudio ABI mismatch

### Symptom
```
OSError: Could not load this library:
  /usr/local/lib/python3.11/dist-packages/torchaudio/lib/libtorchaudio.so
```

### Root cause
The initial Dockerfile pre-installed `torch==2.4.1+cu124` and `torchaudio==2.4.1+cu124`.
When `pip install nemo_toolkit[asr]>=1.23.0` ran afterwards, pip upgraded torch to satisfy
NeMo's transitive dependency requirements — but **torchaudio was not upgraded with it**.
The result: torch 2.10.0+cu128 (new) with torchaudio 2.4.1+cu124 (old).
These are compiled against different torch ABIs and cannot coexist.

### Failed fix attempts
- `pip install --upgrade torchaudio` — only fetches the latest *stable* torchaudio from
  PyPI (2.4.1+cu124). The installed torch (2.10.0+cu128) lives on a different wheel index.

### What actually caused NeMo to install torch 2.10
The `nemo_toolkit[asr]>=1.23.0` requirement with **no upper bound** resolved to
**NeMo 2.6.2** (the current release in early 2026), which in turn requires torch 2.10.

---

## Problem 2 — NeMo 1.x cannot be installed on Python 3.11

When we added `<2.0` to pin NeMo to 1.x, the install failed with:
```
Failed to build 'pyarrow' when installing build dependencies for pyarrow
ModuleNotFoundError: No module named 'Cython'   # (in pyarrow's isolated build env)
```

### Root cause chain (NeMo 1.x only)
```
nemo_toolkit[asr]==1.23.x
  └─ requires datasets<2.0
       └─ datasets 1.x requires pyarrow<4.0.0
            └─ pyarrow 3.0.0 was released Jan 2021
                 └─ Python 3.11 released Oct 2021
                      └─ NO cp311 wheel for pyarrow 3.0.0
                           └─ pip tries to build from source
                                └─ fails (missing Cython, g++, cmake …)
```

Pre-installing Cython, `build-essential`, and even `youtokentome --no-build-isolation`
fixed individual errors but pyarrow 3.0.0 remained unbuildable because its own
`build-system.requires` in the isolated pip environment could not find a compatible
numpy wheel either.

**Conclusion:** NeMo 1.x on Python 3.11 in Docker is a dead end due to pinned old
dependencies with no cp311 wheels. Do not waste time here.

---

## Solution — NeMo 2.x + dynamic torchaudio matching

### Key insight
Accept NeMo 2.x and install torchaudio *after* NeMo, matching whatever torch+CUDA
version NeMo chose, by querying the installed torch at build time.

### requirements.txt
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-multipart>=0.0.12
soundfile>=0.12.1
nemo_toolkit[asr]>=2.0.0
```

### Dockerfile
```dockerfile
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    NEMO_CACHE_DIR=/app/.cache/nemo

RUN apt-get update && apt-get install -y \
        software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
        python3.11 python3.11-dev python3.11-distutils \
        ffmpeg libsndfile1 curl git build-essential \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./

# Step 1: let NeMo install its preferred torch (currently 2.10.0+cu128)
RUN pip install -r requirements.txt

# Step 2: install torchaudio that matches the torch NeMo just installed.
# Query the installed torch for its version string and CUDA tag, then
# pull the matching wheel from the official PyTorch index.
RUN TORCH_VER=$(python3 -c "import torch; print(torch.__version__.split('+')[0])") && \
    TORCH_CUDA=$(python3 -c "import torch, re; v=torch.__version__; \
        m=re.search(r'cu\d+', v); print(m.group() if m else 'cpu')") && \
    pip install "torchaudio==${TORCH_VER}" \
        --index-url "https://download.pytorch.org/whl/${TORCH_CUDA}"

COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Why this works
- NeMo 2.x uses modern packages (pyarrow 23, datasets 4.5, numpy 2.4) that all have
  cp311 wheels — no source compilation needed.
- The dynamic torchaudio step finds `torchaudio==2.10.0+cu128` on
  `https://download.pytorch.org/whl/cu128`, which is ABI-compatible with the installed torch.
- `build-essential` is still needed because a few small NeMo dependencies
  (antlr4-python3-runtime, sox, kaldi-python-io, wget) build pure-Python wheels with
  setuptools and need a C compiler available.

---

## Problem 3 — HuggingFace authentication

### Symptom
```
401 Client Error: Unauthorized for url:
  https://huggingface.co/api/models/nvidia/parakeet-tdt-0.6b
```

### Root cause
NeMo 2.x downloads models via HuggingFace Hub (NeMo 1.x used NGC).
`nvidia/parakeet-tdt-0.6b` is a gated model — users must accept the license
before downloading, even though the model itself is free.

### Fix
1. Accept the license at `https://huggingface.co/nvidia/parakeet-tdt-0.6b`
2. Generate a read token at `https://huggingface.co/settings/tokens`
3. Add to `.env`:
   ```
   HF_TOKEN=hf_your_token_here
   ```

The `env_file: .env` in `docker-compose.yml` passes this to the container automatically.
`huggingface_hub` reads `HF_TOKEN` from the environment with no extra configuration.

---

## Summary

| Problem | Wrong path | Solution |
|---|---|---|
| torchaudio ABI mismatch | Pre-pin torch, upgrade torchaudio after | Let NeMo pick torch; dynamically match torchaudio |
| pyarrow no cp311 wheel | Pin NeMo to 1.x, build from source | Use NeMo 2.x (modern deps, all have cp311 wheels) |
| HuggingFace 401 | — | Accept model license, set HF_TOKEN in .env |

**Rule of thumb:** never pre-install torch before NeMo and then try to fix torchaudio
after the fact. Either pin *everything* (torch + torchaudio + NeMo) to a known-good
combination, or let NeMo choose torch and dynamically match torchaudio to it.
