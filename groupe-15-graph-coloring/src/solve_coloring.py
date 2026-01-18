from ortools.sat.python import cp_model
import networkx as nx


def color_graph(G: nx.Graph, max_colors: int):
    model = cp_model.CpModel()

    # 1 variable "color[node]" par noeud, domaine = [0, max_colors-1]
    color = {v: model.NewIntVar(0, max_colors - 1, f"c_{v}") for v in G.nodes()}

    # contrainte : u et v adjacents => couleurs différentes
    for u, v in G.edges():
        model.Add(color[u] != color[v])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    return {v: solver.Value(color[v]) for v in G.nodes()}


if __name__ == "__main__":
    # Petit graphe de test (triangle) => besoin de 3 couleurs
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (1, 3)])

    sol = color_graph(G, max_colors=3)
    print(sol)
