from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, Optional, Tuple

import networkx as nx

Node = Hashable


@dataclass(frozen=True)
class Instance:
    name: str
    graph: nx.Graph
    pos: Optional[Dict[Node, Tuple[float, float]]] = None


def _norm_name(name: str) -> str:
    # tolérant aux petites erreurs: map.like / map-like / map like -> map_like
    return (
        name.strip()
        .lower()
        .replace(".", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )


def triangle() -> Instance:
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (0, 2)])
    pos = {0: (0, 0), 1: (1, 0), 2: (0.5, 0.9)}
    return Instance("triangle", G, pos)


def cycle(n: int = 8) -> Instance:
    n = max(3, int(n))
    G = nx.cycle_graph(n)
    pos = nx.circular_layout(G)
    return Instance(f"cycle_{n}", G, pos)


def grid(w: int = 4, h: int = 4) -> Instance:
    w = max(2, int(w))
    h = max(2, int(h))
    G = nx.grid_2d_graph(w, h)
    pos = {(x, y): (float(x), float(-y)) for (x, y) in G.nodes()}
    return Instance(f"grid_{w}x{h}", G, pos)


def random_erdos(n: int = 25, p: float = 0.2, seed: int = 1) -> Instance:
    n = max(1, int(n))
    p = float(p)
    p = 0.0 if p < 0.0 else 1.0 if p > 1.0 else p
    seed = int(seed)
    G = nx.erdos_renyi_graph(n=n, p=p, seed=seed)
    pos = nx.spring_layout(G, seed=seed)
    return Instance(f"erdos_n{n}_p{p}_s{seed}", G, pos)


def map_like() -> Instance:
    """Petite 'carte' fictive (régions A..J) pour démo de map coloring."""
    regions = list("ABCDEFGHIJ")
    adj = [
        ("A", "B"), ("A", "C"),
        ("B", "C"), ("B", "D"),
        ("C", "D"), ("C", "E"),
        ("D", "E"), ("D", "F"),
        ("E", "F"), ("E", "G"),
        ("F", "G"), ("F", "H"),
        ("G", "H"), ("G", "I"),
        ("H", "I"), ("H", "J"),
        ("I", "J"),
    ]
    G = nx.Graph()
    G.add_nodes_from(regions)
    G.add_edges_from(adj)

    pos = {
        "A": (0, 2), "B": (1, 2), "C": (0.5, 1.5),
        "D": (1.5, 1.5), "E": (1, 1),
        "F": (2, 1), "G": (1.5, 0.5),
        "H": (2.5, 0.5), "I": (2, 0),
        "J": (3, 0),
    }
    return Instance("map_like", G, pos)


def load_instance(
    name: str,
    n: int = 25,
    p: float = 0.2,
    seed: int = 1,
    w: int = 4,
    h: int = 4,
) -> Instance:
    key = _norm_name(name)

    if key == "triangle":
        return triangle()
    if key == "cycle":
        return cycle(n=n)
    if key == "grid":
        return grid(w=w, h=h)
    if key in ("random", "erdos", "erdos_renyi"):
        return random_erdos(n=n, p=p, seed=seed)
    if key in ("map", "map_like"):
        return map_like()

    raise ValueError(f"Instance inconnue: {name} (triangle/cycle/grid/erdos/map_like)")
