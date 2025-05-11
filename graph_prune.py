import apt
import apt_pkg
import networkx as nx

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
            for or_group in apt_pkg.parse_depends(p.installed.record.get("Provides", "")):
                for virt, *_ in or_group:
                    provides.setdefault(virt, set()).add(p.name)
    for pkg in cache:
        if not pkg.is_installed:
            continue
        for field in ("Depends", "Pre-Depends", "Recommends"):
            dep_str = pkg.installed.record.get(field)
            if not dep_str:
                continue
            for or_group in apt_pkg.parse_depends(dep_str):
                for dep, *_ in or_group:
                    if dep in cache and cache[dep].is_installed:
                        g.add_edge(pkg.name, dep)
                        break
                    if dep in provides:
                        for prov in provides[dep]:
                            g.add_edge(pkg.name, prov)
                        break
    return g

def main():
    manual, auto, cache = get_installed_packages()
    if not auto:
        return
    g = build_dependency_graph(cache)
    reachable = set(manual)
    for m in manual:
        reachable.update(nx.descendants(g, m))
    removable = sorted(auto - reachable)
    if removable:
        print("Removable auto-installed packages:")
        for p in removable:
            print("  ", p)
        print(f"\nTotal: {len(removable)} package(s).")
    else:
        print("✓  All auto-installed packages are still required.")

if __name__ == "__main__":
    main()
