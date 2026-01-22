from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, List, Optional, Tuple

from ortools.sat.python import cp_model

Node = Hashable
Edge = Tuple[Node, Node]


@dataclass(frozen=True)
class SolveInfo:
    status: str
    time_s: float
    conflicts: int
    branches: int


def _status(code: int) -> str:
    return {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.UNKNOWN: "UNKNOWN",
    }.get(code, "UNKNOWN")


def _greedy_hint(nodes: List[Node], edges: List[Edge]) -> Dict[Node, int]:
    adj = {v: set() for v in nodes}
    deg = {v: 0 for v in nodes}
    for u, v in edges:
        if u != v and u in adj and v in adj:
            adj[u].add(v); adj[v].add(u)
            deg[u] += 1; deg[v] += 1

    order = sorted(nodes, key=lambda x: deg[x], reverse=True)
    col: Dict[Node, int] = {}
    for v in order:
        used = {col[u] for u in adj[v] if u in col}
        c = 0
        while c in used:
            c += 1
        col[v] = c
    return col


def solve_k_coloring(
    nodes: List[Node],
    edges: List[Edge],
    k: int,
    timeout_s: float = 5.0,
    num_workers: int = 8,
    symmetry_breaking: bool = True,
    use_hints: bool = True,
) -> Tuple[Optional[Dict[Node, int]], SolveInfo]:
    """
    k-coloring via CP-SAT: c[v] in [0..k-1], and c[u] != c[v] for each edge.
    """
    if k < 1:
        raise ValueError("k must be >= 1")

    nodes = list(nodes)
    if not nodes:
        return {}, SolveInfo("OPTIMAL", 0.0, 0, 0)

    edges = list(edges)

    model = cp_model.CpModel()
    c = {v: model.NewIntVar(0, k - 1, f"c_{v}") for v in nodes}

    # Symmetry breaking: fix first node color to 0
    if symmetry_breaking:
        model.Add(c[nodes[0]] == 0)

    # Constraints
    for u, v in edges:
        if u != v and u in c and v in c:
            model.Add(c[u] != c[v])

    # Hints from greedy (often speeds up)
    if use_hints:
        hint = _greedy_hint(nodes, edges)
        if max(hint.values(), default=-1) < k:
            for v, hv in hint.items():
                model.AddHint(c[v], int(hv))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(timeout_s)
    solver.parameters.num_search_workers = int(num_workers)

    st = solver.Solve(model)
    info = SolveInfo(
        status=_status(st),
        time_s=float(solver.WallTime()),
        conflicts=int(solver.NumConflicts()),
        branches=int(solver.NumBranches()),
    )

    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {v: int(solver.Value(c[v])) for v in nodes}, info
    return None, info


def solve_min_coloring(
    nodes: List[Node],
    edges: List[Edge],
    # bornes
    k_min: int = 1,
    k_max: Optional[int] = None,
    # solve params
    timeout_per_k_s: float = 3.0,
    num_workers: int = 8,
    symmetry_breaking: bool = True,
) -> Tuple[Optional[int], Optional[Dict[Node, int]], List[Tuple[int, SolveInfo]]]:
    """
    Minimum coloring by trying k from k_min to k_max.
    Optimisation: start from a better lower bound (k_min) and stop at k_max.
    """
    nodes = list(nodes)
    if not nodes:
        return 0, {}, []

    if k_max is None:
        k_max = len(nodes)

    k_min = max(1, int(k_min))
    k_max = min(int(k_max), len(nodes))
    if k_min > k_max:
        return None, None, []

    log: List[Tuple[int, SolveInfo]] = []
    for k in range(k_min, k_max + 1):
        sol, info = solve_k_coloring(
            nodes=nodes,
            edges=edges,
            k=k,
            timeout_s=timeout_per_k_s,
            num_workers=num_workers,
            symmetry_breaking=symmetry_breaking,
            use_hints=True,
        )
        log.append((k, info))
        if sol is not None:
            return k, sol, log

    return None, None, log
