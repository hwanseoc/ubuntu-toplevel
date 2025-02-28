from apt import cache
import requests

response = requests.get('https://old-releases.ubuntu.com/releases/noble/ubuntu-24.04.1-desktop-amd64.manifest')

assert response.ok
manifest = set(line.split('\t')[0] for line in response.text.split('\n'))
manual = set(pkg.name for pkg in cache.Cache() if pkg.is_installed and not pkg.is_auto_installed)
for name in sorted(manual - manifest):
    print(name)
