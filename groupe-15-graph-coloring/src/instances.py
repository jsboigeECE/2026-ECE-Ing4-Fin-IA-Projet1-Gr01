from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Hashable, List, Tuple, Optional
import networkx as nx

Node = Hashable
Edge = Tuple[Node, Node]


@dataclass
class Instance:
    name: str
    graph: nx.Graph
    pos: Optional[Dict[Node, Tuple[float, float]]] = None


def triangle() -> Instance:
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (0, 2)])
    pos = {0: (0, 0), 1: (1, 0), 2: (0.5, 0.9)}
    return Instance("triangle", G, pos)


def cycle(n: int = 8) -> Instance:
    G = nx.cycle_graph(n)
    pos = nx.circular_layout(G)
    return Instance(f"cycle_{n}", G, pos)


def grid(w: int = 4, h: int = 4) -> Instance:
    # Noeuds = tuples (x,y)
    G = nx.grid_2d_graph(w, h)
    pos = {(x, y): (x, -y) for (x, y) in G.nodes()}
    return Instance(f"grid_{w}x{h}", G, pos)


def random_erdos(n: int = 25, p: float = 0.2, seed: int = 1) -> Instance:
    G = nx.erdos_renyi_graph(n=n, p=p, seed=seed)
    pos = nx.spring_layout(G, seed=seed)
    return Instance(f"erdos_n{n}_p{p}_s{seed}", G, pos)


def map_like() -> Instance:
    """
    Petite 'carte' fictive (régions A..J) avec une structure planar-ish.
    Très bien pour montrer 'map coloring' sans dépendances externes.
    """
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

    # positions fixes pour un rendu "carte"
    pos = {
        "A": (0, 2), "B": (1, 2), "C": (0.5, 1.5),
        "D": (1.5, 1.5), "E": (1, 1),
        "F": (2, 1), "G": (1.5, 0.5),
        "H": (2.5, 0.5), "I": (2, 0),
        "J": (3, 0),
    }
    return Instance("map_like", G, pos)


def load_instance(name: str, n: int, p: float, seed: int, w: int, h: int) -> Instance:
    name = name.lower()
    if name == "triangle":
        return triangle()
    if name == "cycle":
        return cycle(n=max(3, n))
    if name == "grid":
        return grid(w=max(2, w), h=max(2, h))
    if name in ("random", "erdos", "erdos_renyi"):
        return random_erdos(n=max(1, n), p=p, seed=seed)
    if name in ("map", "map_like"):
        return map_like()
    raise ValueError(f"Instance inconnue: {name}")