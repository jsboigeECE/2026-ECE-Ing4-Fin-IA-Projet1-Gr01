from __future__ import annotations
from typing import Dict, Hashable, Optional, Tuple
import os
import networkx as nx
import matplotlib.pyplot as plt

Node = Hashable


def _palette():
    # Palette simple, réutilisée si k > len(palette)
    return [
        "#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2",
        "#B279A2", "#FF9DA6", "#9D755D", "#BAB0AC", "#8CD17D",
    ]


def draw_coloring(
    G: nx.Graph,
    coloring: Dict[Node, int],
    pos: Optional[Dict[Node, Tuple[float, float]]] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = False,
):
    pal = _palette()
    node_colors = []
    for v in G.nodes():
        c = coloring.get(v, 0)
        node_colors.append(pal[c % len(pal)])

    if pos is None:
        pos = nx.spring_layout(G, seed=1)

    plt.figure(figsize=(7, 5))
    nx.draw_networkx(
        G,
        pos=pos,
        with_labels=True,
        node_color=node_colors,
        edgecolors="black",
        font_size=10,
    )
    if title:
        plt.title(title)

    plt.axis("off")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=200)

    if show:
        plt.show()

    plt.close()