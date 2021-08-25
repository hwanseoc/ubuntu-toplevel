# %%

from apt import cache
import requests
import re

def replace_arch(name):
    name = re.sub('(:[a-zA-Z0-9_]*)', '', name)
    return name

response = requests.get('https://releases.ubuntu.com/21.04/ubuntu-21.04-desktop-amd64.manifest')
text = response.text
manifest = [
    replace_arch(line.split('\t')[0]) for line in text.split('\n')
]

installed = [
    replace_arch(pkg.name) for pkg in cache.Cache() if pkg.is_installed
]

manual = [
    replace_arch(pkg.name) for pkg in cache.Cache() if pkg.is_installed and not pkg.is_auto_installed
]

depends = [
    replace_arch(dep_pkg.name)
    for pkg in cache.Cache() if pkg.is_installed
    for dep in pkg.installed.get_dependencies('PreDepends', 'Depends', 'Recommends')
    for dep_pkg in dep
]

depends_edge = [
    [replace_arch(pkg.name), replace_arch(dep_pkg.name)]
    for pkg in cache.Cache() if pkg.is_installed
    for dep in pkg.installed.get_dependencies('PreDepends', 'Depends', 'Recommends')
    for dep_pkg in dep
]

# %%
manual_not_manifest = [name for name in manual if name not in manifest]
manual_not_manifest = sorted(manual_not_manifest)

for name in manual_not_manifest:
    # if name in depends:
    #     print(name)
    if '-ko' not in name and '-cjk-' not in name:
            print(name)
