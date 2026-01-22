from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, Hashable, Optional, Tuple

import networkx as nx

from instances import load_instance
from heuristics import greedy_coloring, dsatur_coloring
from solve_coloring import solve_k_coloring, solve_min_coloring
from viz import draw_plain, draw_coloring

# benchmark est optionnel: si absent, on n'explose pas
try:
    from benchmark import run_benchmark
except Exception:
    run_benchmark = None  # type: ignore

Node = Hashable


# ------------------- IO helpers -------------------
def ensure_parent(path: Optional[str]) -> Optional[Path]:
    if not path:
        return None
    p = Path(path)
    if p.parent and str(p.parent) != ".":
        p.parent.mkdir(parents=True, exist_ok=True)
    return p


def save_json(path: str, payload: dict) -> None:
    p = ensure_parent(path)
    if p is None:
        return
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def make_before_path(save_fig: Optional[str]) -> Optional[str]:
    if not save_fig:
        return None
    root, ext = os.path.splitext(save_fig)
    return f"{root}_before{ext or '.png'}"


# ------------------- Metrics -------------------
def is_valid_coloring(G: nx.Graph, coloring: Dict[Node, int]) -> bool:
    return all(coloring.get(u) != coloring.get(v) for u, v in G.edges())


def colors_used(coloring: Dict[Node, int]) -> int:
    return len(set(coloring.values())) if coloring else 0


# ------------------- Bounds (optimization) -------------------
def lower_bound_clique(G: nx.Graph) -> int:
    """
    Lower bound via clique number.
    - For our project sizes, networkx clique_number is ok.
    - If it fails for any reason, fallback to 1.
    """
    try:
        # exact clique number (can be heavy on very large graphs)
        return max(1, int(nx.graph_clique_number(G)))
    except Exception:
        return 1


def upper_bound_dsatur(G: nx.Graph) -> int:
    col = dsatur_coloring(G)
    return max(1, colors_used(col))


# ------------------- Interactive helpers -------------------
def ask_str(prompt: str, default: str) -> str:
    s = input(f"{prompt} [{default}] : ").strip()
    return s if s else default


def ask_int(prompt: str, default: int) -> int:
    s = input(f"{prompt} [{default}] : ").strip()
    return int(s) if s else default


def ask_float(prompt: str, default: float) -> float:
    s = input(f"{prompt} [{default}] : ").strip()
    return float(s) if s else default


def ask_bool(prompt: str, default: bool) -> bool:
    d = "o" if default else "n"
    s = input(f"{prompt} (o/n) [{d}] : ").strip().lower()
    if not s:
        return default
    return s in ("o", "oui", "y", "yes")


def interactive_config() -> dict:
    print("\n=== Coloration de graphe / carte (mode interactif) ===")
    print("Instances possibles : triangle, cycle, grid, erdos, map_like")
    instance = ask_str("Choisis une instance", "map_like")

    n = ask_int("n (cycle/erdos)", 25)
    p = ask_float("p (erdos)", 0.2)
    seed = ask_int("seed", 1)
    w = ask_int("w (grid)", 6)
    h = ask_int("h (grid)", 6)

    print("\nMéthodes :")
    print("  - cp_k      : OR-Tools CP-SAT avec k fixé")
    print("  - cp_min    : OR-Tools CP-SAT (cherche le minimum k) + bornes (LB/UB)")
    print("  - greedy    : heuristique gloutonne")
    print("  - dsatur    : heuristique DSATUR")
    print("  - compare   : compare greedy/dsatur/cp_min (bonus 1 + 6)")
    print("  - benchmark : benchmark auto -> CSV (bonus 5)")
    method = ask_str("Choisis une méthode", "cp_min").lower()

    timeout = ask_float("timeout (secondes) [cp_* ou benchmark]", 3.0)

    k = None
    if method == "cp_k":
        k = ask_int("k (nb max de couleurs)", 4)

    show = ask_bool("Afficher les graphes (avant puis après) ?", False)
    save_fig = ask_str("Chemin image (ex: outputs/map.png) (Entrée = rien)", "")
    save_fig = save_fig if save_fig else None
    save_js = ask_str("Chemin JSON (ex: outputs/map.json) (Entrée = rien)", "")
    save_js = save_js if save_js else None

    return {
        "instance": instance, "n": n, "p": p, "seed": seed, "w": w, "h": h,
        "method": method, "k": k, "timeout": timeout,
        "show": show, "save_fig": save_fig, "save_json": save_js
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Graph/Map Coloring (interactive by default).")
    p.add_argument("--no-interactive", action="store_true")
    p.add_argument("--instance", type=str, default=None)
    p.add_argument("--n", type=int, default=25)
    p.add_argument("--p", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--w", type=int, default=6)
    p.add_argument("--h", type=int, default=6)

    p.add_argument("--method", type=str, default=None,
                   help="cp_k/cp_min/greedy/dsatur/compare/benchmark")
    p.add_argument("--k", type=int, default=None)
    p.add_argument("--timeout", type=float, default=3.0)
    p.add_argument("--show", action="store_true")
    p.add_argument("--save-fig", type=str, default=None)
    p.add_argument("--save-json", type=str, default=None)
    return p


# ------------------- Runners -------------------
def draw_before_after(
    G: nx.Graph,
    pos,
    inst_name: str,
    title_after: str,
    coloring: Optional[Dict[Node, int]],
    show: bool,
    save_fig: Optional[str],
):
    if not (show or save_fig):
        return

    before_path = make_before_path(save_fig)
    if before_path:
        ensure_parent(before_path)

    draw_plain(G, pos=pos, title=f"{inst_name} | BEFORE", save_path=before_path, show=show)

    if coloring is not None:
        if save_fig:
            ensure_parent(save_fig)
        draw_coloring(G, coloring, pos=pos, title=title_after, save_path=save_fig, show=show)


def run_method(
    G: nx.Graph,
    pos,
    inst_name: str,
    method: str,
    timeout: float,
    k: Optional[int],
    show: bool,
    save_fig: Optional[str],
    save_json_path: Optional[str],
):
    nodes = list(G.nodes())
    edges = list(G.edges())

    coloring: Optional[Dict[Node, int]] = None
    info: dict = {}
    used = 0
    valid = False

    if method == "greedy":
        t0 = time.perf_counter()
        coloring = greedy_coloring(G)
        dt = time.perf_counter() - t0
        info = {"status": "OK", "time_s": dt}

    elif method == "dsatur":
        t0 = time.perf_counter()
        coloring = dsatur_coloring(G)
        dt = time.perf_counter() - t0
        info = {"status": "OK", "time_s": dt}

    elif method == "cp_k":
        if k is None:
            raise ValueError("cp_k nécessite k.")
        coloring, si = solve_k_coloring(nodes, edges, k=k, timeout_s=timeout)
        info = {"status": si.status, "time_s": si.time_s, "conflicts": si.conflicts, "branches": si.branches}

    elif method == "cp_min":
        # 🔥 OPTIMISATION: bornes LB/UB
        lb = lower_bound_clique(G)
        ub = upper_bound_dsatur(G)
        best_k, coloring, log = solve_min_coloring(
            nodes, edges,
            k_min=lb,
            k_max=ub,                 # stop at DSATUR upper bound
            timeout_per_k_s=timeout,
        )
        info = {
            "lb_clique": lb,
            "ub_dsatur": ub,
            "k_found": best_k,
            "log": [{"k": kk, "status": s.status, "time_s": s.time_s} for kk, s in log],
        }

    else:
        raise ValueError(f"Méthode inconnue: {method}")

    if coloring is not None:
        used = colors_used(coloring)
        valid = is_valid_coloring(G, coloring)

    print("\n--- Résultat ---")
    print(f"Instance: {inst_name} | nodes={G.number_of_nodes()} edges={G.number_of_edges()}")
    print(f"Method: {method}")
    if method == "cp_k":
        print(f"k={k} | status={info.get('status')} | colors_used={used} | valid={valid}")
    elif method == "cp_min":
        print(f"LB={info.get('lb_clique')} UB={info.get('ub_dsatur')} | k*={info.get('k_found')} | colors_used={used} | valid={valid}")
    else:
        print(f"colors_used={used} | valid={valid}")

    title_after = f"{inst_name} | {method} | colors={used} | valid={valid}"
    draw_before_after(G, pos, inst_name, title_after, coloring, show, save_fig)

    if save_json_path:
        payload = {
            "instance": inst_name,
            "method": method,
            "k": k,
            "valid": valid,
            "colors_used": used,
            "info": info,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_json(save_json_path, payload)
        print(f"JSON sauvegardé -> {save_json_path}")


def run_compare(
    inst,
    timeout: float,
    show: bool,
    save_fig: Optional[str],
    save_json_path: Optional[str],
):
    methods = ["greedy", "dsatur", "cp_min"]
    base_fig = save_fig
    base_json = save_json_path

    for m in methods:
        fig_path = None
        js_path = None
        if base_fig:
            root, ext = os.path.splitext(base_fig)
            fig_path = f"{root}_{m}{ext or '.png'}"
        if base_json:
            root, ext = os.path.splitext(base_json)
            js_path = f"{root}_{m}{ext or '.json'}"

        # Afficher seulement pour le dernier (évite 6 fenêtres)
        show_now = show and (m == methods[-1])

        print(f"\n=== RUN {m} ===")
        run_method(
            inst.graph, inst.pos, inst.name,
            method=m, timeout=timeout, k=None,
            show=show_now,
            save_fig=fig_path,
            save_json_path=js_path,
        )


def run_bench(timeout: float):
    if run_benchmark is None:
        raise SystemExit("benchmark.py manquant: crée src/benchmark.py ou enlève la méthode benchmark.")
    out_csv = "outputs/benchmark.csv"
    print("\n=== BENCHMARK ===")
    print(f"Le CSV sera écrit ici : {out_csv}")
    rows = run_benchmark(out_csv=out_csv, timeout_cp_min=timeout)
    print(f"Benchmark terminé ✅ ({len(rows)} lignes) -> {out_csv}")


def main() -> None:
    args = build_parser().parse_args()

    if not args.no_interactive and args.method is None and args.instance is None:
        cfg = interactive_config()
        method = cfg["method"]
        timeout = float(cfg["timeout"])
        show = bool(cfg["show"])
        save_fig = cfg["save_fig"]
        save_js = cfg["save_json"]
        k = cfg["k"]

        # ✅ BENCHMARK: ne dépend plus d'une instance (anti-crash)
        if method == "benchmark":
            run_bench(timeout)
            return

        inst = load_instance(cfg["instance"], n=cfg["n"], p=cfg["p"], seed=cfg["seed"], w=cfg["w"], h=cfg["h"])

    else:
        if args.method is None:
            raise SystemExit("Mode non interactif: --method requis.")
        method = args.method.lower()
        timeout = float(args.timeout)
        show = bool(args.show)
        save_fig = args.save_fig
        save_js = args.save_json
        k = args.k

        if method == "benchmark":
            run_bench(timeout)
            return

        if args.instance is None:
            raise SystemExit("Mode non interactif: --instance requis sauf pour benchmark.")
        inst = load_instance(args.instance, n=args.n, p=args.p, seed=args.seed, w=args.w, h=args.h)

    if method == "compare":
        run_compare(inst, timeout=timeout, show=show, save_fig=save_fig, save_json_path=save_js)
    else:
        run_method(inst.graph, inst.pos, inst.name, method=method, timeout=timeout, k=k, show=show, save_fig=save_fig, save_json_path=save_js)


if __name__ == "__main__":
    main()
