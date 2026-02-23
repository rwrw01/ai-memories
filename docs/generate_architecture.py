"""
Generate architecture diagram for the Memories project.
Update PHASE_STATUS below when a phase completes, then re-run.

Requirements:
    pip install diagrams
    sudo apt install graphviz   # or: brew install graphviz

Usage:
    python docs/generate_architecture.py
    # Outputs: docs/architecture.png
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.generic.device import Mobile
from diagrams.programming.framework import Svelte, FastAPI
from diagrams.onprem.container import Docker
from diagrams.onprem.workflow import Airflow   # placeholder for n8n

# ── Phase completion status ──────────────────────────────────────────────────
# Set True when a phase is merged to main.
PHASE_STATUS = {
    1: True,   # PWA basis
    2: True,   # STT Parakeet
    3: True,   # TTS Parkiet + Piper
    4: False,  # LLM Ollama
    5: False,  # News briefing
    6: False,  # Calendar
    7: False,  # Hardening
}

# ── Graphviz styling helpers ─────────────────────────────────────────────────
DONE_NODE   = {"style": "filled", "fillcolor": "#d4edda", "fontcolor": "#155724"}
PENDING_NODE = {"style": "filled", "fillcolor": "#e2e3e5", "fontcolor": "#6c757d"}

DONE_CLUSTER   = {"bgcolor": "#f0fff4", "color": "#28a745", "fontcolor": "#155724"}
PENDING_CLUSTER = {"bgcolor": "#f8f9fa", "color": "#adb5bd", "fontcolor": "#6c757d"}

def node_style(done: bool) -> dict:
    return DONE_NODE if done else PENDING_NODE

def cluster_style(done: bool) -> dict:
    return DONE_CLUSTER if done else PENDING_CLUSTER


# ── Diagram ──────────────────────────────────────────────────────────────────
graph_attr = {
    "fontsize": "13",
    "bgcolor": "white",
    "pad": "0.6",
    "splines": "ortho",
    "nodesep": "0.7",
    "ranksep": "1.0",
}

with Diagram(
    "Memories — Local AI Assistant",
    filename="docs/architecture",
    outformat="png",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    iphone = Mobile("iPhone\n(Safari PWA)", **node_style(PHASE_STATUS[1]))

    with Cluster("Tailscale Funnel (HTTPS)"):

        with Cluster(
            f"memories/ — Phase 1{'  ✓' if PHASE_STATUS[1] else ''}",
            graph_attr=cluster_style(PHASE_STATUS[1]),
        ):
            frontend = Svelte("SvelteKit\n:3000", **node_style(PHASE_STATUS[1]))

        with Cluster(
            f"memories/backend — proxy  :8000",
            graph_attr=cluster_style(PHASE_STATUS[2]),
        ):
            backend = FastAPI("FastAPI\n:8000", **node_style(PHASE_STATUS[2]))

        with Cluster(
            "services/ — ai-net (Docker)",
            graph_attr={"bgcolor": "#fffef0", "color": "#ffc107"},
        ):
            with Cluster(
                f"Phase 2 — STT{'  ✓' if PHASE_STATUS[2] else ''}",
                graph_attr=cluster_style(PHASE_STATUS[2]),
            ):
                stt = Docker("Parakeet-TDT\n:8001  GPU", **node_style(PHASE_STATUS[2]))

            with Cluster(
                f"Phase 3 — TTS{'  ✓' if PHASE_STATUS[3] else ''}",
                graph_attr=cluster_style(PHASE_STATUS[3]),
            ):
                tts = Docker("Parkiet 1.6B\n:8002  GPU", **node_style(PHASE_STATUS[3]))
                piper = Docker("Piper nl_BE\n(fallback, CPU)", **node_style(PHASE_STATUS[3]))

            with Cluster(
                f"Phase 4 — LLM{'  ✓' if PHASE_STATUS[4] else ''}",
                graph_attr=cluster_style(PHASE_STATUS[4]),
            ):
                llm = Docker("Ollama\n:11434", **node_style(PHASE_STATUS[4]))

            with Cluster(
                f"Phase 5/6 — Orchestration{'  ✓' if PHASE_STATUS[5] else ''}",
                graph_attr=cluster_style(PHASE_STATUS[5]),
            ):
                n8n = Airflow("n8n\n(cron + workflows)", **node_style(PHASE_STATUS[5]))

    # Connections
    iphone >> Edge(label="HTTPS") >> frontend
    frontend >> Edge(label="REST") >> backend
    backend >> Edge(label="/api/stt", color="#28a745" if PHASE_STATUS[2] else "#adb5bd") >> stt
    backend >> Edge(label="/api/tts", color="#28a745" if PHASE_STATUS[3] else "#adb5bd") >> tts
    backend >> Edge(label="/api/chat", color="#28a745" if PHASE_STATUS[4] else "#adb5bd") >> llm
    tts >> Edge(label="fallback", style="dashed") >> piper
    n8n >> Edge(label="trigger", style="dashed") >> backend


if __name__ == "__main__":
    print("Architecture diagram generated: docs/architecture.png")
    print("Phase status:")
    for phase, done in PHASE_STATUS.items():
        print(f"  Phase {phase}: {'✓ Done' if done else '○ Pending'}")
