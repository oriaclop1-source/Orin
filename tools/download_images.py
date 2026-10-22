#!/usr/bin/env python3
"""Download every image the site uses from Shopify into assets/img/, and point
the site at the local copies. Run this BEFORE cancelling the Shopify plan —
Shopify's image links stop working once the store is closed.

Usage (from the repo folder, Python 3.8+, no extra packages):
    python3 tools/download_images.py

It is safe to run again; files that already exist are skipped.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOP_FILES = "https://cdn.shopify.com/s/files/1/0843/2746/5200/"
THEME_ASSET_URLS = [
    "https://cdn.shopify.com/s/files/1/0843/2746/5200/t/8/assets/{}",
    "https://4ynmhe-pk.myshopify.com/cdn/shop/t/8/assets/{}",
]
THEME_ASSETS = ["logo.png", "world.png", "kids.png", "mature.png", "home.png", "house.png", "special.png",
                "retro.png", "noam.png", "mystery.png", "english.png", "spain.png", "italy.png",
                "israel.png", "stussy.png", "rest.png"]


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as res, open(dest + ".part", "wb") as out:
            out.write(res.read())
        os.replace(dest + ".part", dest)
        return True
    except Exception as exc:  # keep going; report at the end
        print(f"  failed: {url} ({exc})")
        if os.path.exists(dest + ".part"):
            os.remove(dest + ".part")
        return False


def local_name(url):
    path = urllib.parse.urlparse(url).path
    base = os.path.basename(path)
    stem, ext = os.path.splitext(base)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-")[:60] or "image"
    digest = hashlib.sha1(path.encode()).hexdigest()[:8]
    return f"{safe}-{digest}{ext.lower() or '.jpg'}"


def main():
    with open(os.path.join(ROOT, "export/shopify-products.json"), encoding="utf-8") as f:
        products = json.load(f)
    with open(os.path.join(ROOT, "assets/config.js"), encoding="utf-8") as f:
        config = f.read()

    urls = set()
    for p in products:
        for m in p["media"]["nodes"]:
            if m.get("image"):
                urls.add(m["image"]["url"].split("?")[0])
    customer_base = re.search(r"customerPhotoBase:\s*'([^']+)'", config).group(1)
    customer_urls = []
    for name in re.search(r"customerPhotos:\s*\[(.*?)\]", config, re.S).group(1).split(","):
        name = name.strip().strip("'\"")
        if name and customer_base.startswith("http"):
            customer_urls.append(customer_base + name)
    urls.update(customer_urls)
    banner = re.search(r"image:\s*'(https://cdn\.shopify\.com[^']+)'", config)
    if banner:
        urls.add(banner.group(1))

    image_map = {}
    failed = 0
    print(f"Downloading {len(urls)} images...")
    for i, url in enumerate(sorted(urls), 1):
        rel = "assets/img/files/" + local_name(url)
        if fetch(url, os.path.join(ROOT, rel)):
            image_map[url] = rel
        else:
            failed += 1
        if i % 50 == 0:
            print(f"  {i}/{len(urls)}")

    print("Downloading theme images (logo, categories, size charts)...")
    theme_ok = True
    for name in THEME_ASSETS:
        dest = os.path.join(ROOT, "assets/img/theme", name)
        if not any(fetch(u.format(name), dest) for u in THEME_ASSET_URLS):
            failed += 1
            theme_ok = False

    with open(os.path.join(ROOT, "data/image-map.json"), "w", encoding="utf-8") as f:
        json.dump(image_map, f, ensure_ascii=False, indent=0)

    # Point the site at the local files.
    if theme_ok:
        config = config.replace("themeAssetBase: 'https://cdn.shopify.com/s/files/1/0843/2746/5200/t/8/assets/'",
                                "themeAssetBase: 'assets/img/theme/'")
    if banner and banner.group(1) in image_map:
        config = config.replace(banner.group(1), image_map[banner.group(1)])
    if customer_urls and all(u in image_map for u in customer_urls):
        for url in customer_urls:
            config = config.replace("'" + url[len(customer_base):] + "'", "'" + image_map[url][len("assets/img/files/"):] + "'")
        config = config.replace(f"customerPhotoBase: '{customer_base}'", "customerPhotoBase: 'assets/img/files/'")
    with open(os.path.join(ROOT, "assets/config.js"), "w", encoding="utf-8") as f:
        f.write(config)

    subprocess.check_call([sys.executable, os.path.join(ROOT, "tools/build_catalog.py")])
    print("Done." if not failed else f"Done, but {failed} downloads failed — run the script again.")


if __name__ == "__main__":
    main()
