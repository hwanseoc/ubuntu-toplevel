# %%

from apt import cache
import requests
import re

def replace_arch(name):
    name = re.sub('(:[a-zA-Z0-9_]*)', '', name)
    return name

response = requests.get('https://releases.ubuntu.com/22.04.1/ubuntu-22.04.1-desktop-amd64.manifest')
text = response.text
manifest = [
    replace_arch(line.split('\t')[0]) for line in text.split('\n')
]

# installed = [
#     replace_arch(pkg.name) for pkg in cache.Cache() if pkg.is_installed
# ]

manual = [
    replace_arch(pkg.name) for pkg in cache.Cache() if pkg.is_installed and not pkg.is_auto_installed
]

# depends = [
#     replace_arch(dep_pkg.name)
#     for pkg in cache.Cache() if pkg.is_installed
#     for dep in pkg.installed.get_dependencies('PreDepends', 'Depends', 'Recommends')
#     for dep_pkg in dep
# ]

# depends_edge = [
#     [replace_arch(pkg.name), replace_arch(dep_pkg.name)]
#     for pkg in cache.Cache() if pkg.is_installed
#     for dep in pkg.installed.get_dependencies('PreDepends', 'Depends', 'Recommends')
#     for dep_pkg in dep
# ]

# %%
manual_not_manifest = sorted([name for name in manual if name not in manifest])

for name in manual_not_manifest:
    print(name)
