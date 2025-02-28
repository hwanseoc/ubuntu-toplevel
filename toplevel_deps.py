import apt
import requests

def get_manual_installed_packages():
    """
    Returns a dict mapping package names to apt.Package objects 
    for packages that are installed manually.
    """
    cache = apt.Cache()
    return {pkg.name: pkg for pkg in cache if pkg.is_installed and not pkg.is_auto_installed}

def get_manual_diff_from_manifest(manual):
    """
    Fetch the manifest file from the given URL and remove those packages,
    returning only the packages that are in the manual set but not mentioned
    in the manifest.
    """
    url = 'https://old-releases.ubuntu.com/releases/noble/ubuntu-24.04.1-desktop-amd64.manifest'
    response = requests.get(url)
    response.raise_for_status()
    manifest = set(line.split('\t')[0] for line in response.text.splitlines() if line.strip())
    # Only keep packages that are not in the manifest
    return {name: pkg for name, pkg in manual.items() if name not in manifest}

def find_dependency_packages(packages):
    """
    For the given dict of packages (name -> Package), walk through the
    dependencies of each package (taken from its 'installed' version) and,
    if one of the dependency names is also in packages, record that dependency.
    
    Returns a dict mapping package names (that are dependencies inside the list)
    to a set of packages which depend on them.
    """
    # For each package in our list, get its dependencies that are also in the list.
    dep_map = {}
    for name, pkg in packages.items():
        deps = set()
        if pkg.installed:
            # pkg.installed.dependencies is a list of dependency groups (for alternatives)
            for dep_group in pkg.installed.dependencies:
                for alt in dep_group:
                    if alt.name in packages:
                        deps.add(alt.name)
        if deps:
            dep_map[name] = deps

    # Invert the dependency mapping.  For each package in the list,
    # record which other packages depend on it.
    inverted = {}
    for pkg, deps in dep_map.items():
        for dep in deps:
            inverted.setdefault(dep, set()).add(pkg)
    return inverted

if __name__ == '__main__':
    manual = get_manual_installed_packages()
    packages = get_manual_diff_from_manifest(manual)
    
    dependency_dict = find_dependency_packages(packages)
    
    if dependency_dict:
        print("The following packages in your list are dependencies of other packages:")
        for dep, dependents in sorted(dependency_dict.items()):
            print(f"{dep} - required by: {', '.join(sorted(dependents))}")
    else:
        print("No package in the list is a dependency of another.")
