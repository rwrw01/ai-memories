"""
Generate architecture diagram for the Memories project.

Requirements:
    pip install diagrams
    sudo apt install graphviz   # or: brew install graphviz

Usage:
    python docs/generate_architecture.py
    # Outputs: docs/architecture.png
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.generic.device import Mobile
from diagrams.generic.network import Firewall
from diagrams.programming.framework import Svelte, FastAPI
from diagrams.onprem.container import Docker
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Nginx

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5",
}

cluster_attr = {
    "fontsize": "12",
}

with Diagram(
    "Memories — Local AI Assistant",
    filename="docs/architecture",
    outformat="png",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    iphone = Mobile("iPhone\n(Safari PWA)")

    with Cluster("Tailscale Funnel (HTTPS)"):
        with Cluster("memories/ — Docker Compose", graph_attr=cluster_attr):
            frontend = Svelte("SvelteKit\n:3000")
            backend = FastAPI("FastAPI Proxy\n:8000")

        with Cluster("services/ — Docker Compose  ai-net", graph_attr=cluster_attr):
            stt = Docker("Parakeet STT\n:8001  GPU")
            tts = Docker("Parkiet TTS\n:8002  GPU")
            piper = Docker("Piper TTS\n(fallback, CPU)")

    iphone >> Edge(label="HTTPS") >> frontend
    frontend >> Edge(label="REST") >> backend
    backend >> Edge(label="/api/stt") >> stt
    backend >> Edge(label="/api/tts") >> tts
    tts >> Edge(label="fallback", style="dashed") >> piper
