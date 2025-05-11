import apt
import apt_pkg
import networkx as nx
from collections import deque

def get_installed_packages():
    apt_pkg.init()
    cache = apt.Cache()
    manual = {p.name for p in cache if p.is_installed and not p.is_auto_installed}
    auto = {p.name for p in cache if p.is_installed and p.is_auto_installed}
    return manual, auto, cache

def build_dependency_graph(cache):
    g = nx.DiGraph()
    g.add_nodes_from(p.name for p in cache if p.is_installed)
    provides = {}
    for p in cache:
        if p.is_installed:
            for group in apt_pkg.parse_depends(p.installed.record.get("Provides", "")):
                for virt, *_ in group:
                    provides.setdefault(virt, set()).add(p.name)
    for p in cache:
        if not p.is_installed:
            continue
        for field in ("Depends", "Pre-Depends", "Recommends"):
            dep_str = p.installed.record.get(field)
            if not dep_str:
                continue
            for group in apt_pkg.parse_depends(dep_str):
                for dep, *_ in group:
                    if dep in cache and cache[dep].is_installed:
                        g.add_edge(p.name, dep)
                        break
                    if dep in provides:
                        for prov in provides[dep]:
                            g.add_edge(p.name, prov)
                        break
    return g

def shortest_paths(g, roots):
    paths = {r: [r] for r in roots}
    q = deque(roots)
    while q:
        n = q.popleft()
        for succ in g.successors(n):
            if succ not in paths:
                paths[succ] = paths[n] + [succ]
                q.append(succ)
    return paths

def main():
    manual, _, cache = get_installed_packages()
    if not manual:
        print("No manually-installed packages detected.")
        return
    g = build_dependency_graph(cache)
    paths = shortest_paths(g, manual)
    for pkg in sorted(g.nodes()):
        if pkg in paths:
            chain = list(reversed(paths[pkg]))
            chain[-1] += " [installed]"
            print(" - ".join(chain))
        else:
            print(f"{pkg} is not reachable from a manually-installed package")

if __name__ == "__main__":
    main()
