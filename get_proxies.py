# get_proxies.py
import urllib.request
import re

sources = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
]

proxies = set()
for url in sources:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            for line in content.splitlines():
                line = line.strip()
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}$', line):
                    proxies.add(f"http://{line}")
    except:
        pass

with open("proxies.txt", "w") as f:
    f.write("\n".join(proxies))

print(f"تم حفظ {len(proxies)} بروكسي في proxies.txt")
