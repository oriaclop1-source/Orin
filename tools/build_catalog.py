#!/usr/bin/env python3
"""Build data/catalog.json (what the site loads) from the raw Shopify export.

Usage:  python3 tools/build_catalog.py
Input:  export/shopify-products.json, export/shopify-collections.json
Output: data/catalog.json

If tools/download_images.py has been run, image URLs are rewritten to the
local copies listed in data/image-map.json.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def main():
    products = load("export/shopify-products.json")
    collections = load("export/shopify-collections.json")

    image_map = {}
    map_path = os.path.join(ROOT, "data/image-map.json")
    if os.path.exists(map_path):
        image_map = load("data/image-map.json")

    def img(url):
        return image_map.get(url.split("?")[0], url)

    out_products = []
    for p in products:
        if p["status"] != "ACTIVE":
            continue
        options = [o for o in p["options"] if not (o["name"] == "Title" and o["values"] == ["Default Title"])]
        variants = []
        for v in p["variants"]["nodes"]:
            row = {
                "o": [so["value"] for so in v["selectedOptions"]][: len(options)],
                "p": float(v["price"]),
            }
            if v.get("compareAtPrice") and float(v["compareAtPrice"]) > float(v["price"]):
                row["c"] = float(v["compareAtPrice"])
            if not v["availableForSale"]:
                row["x"] = 1
            variants.append(row)
        out_products.append({
            "h": p["handle"],
            "t": p["title"],
            "d": p["descriptionHtml"],
            "s": p.get("templateSuffix") or "",
            "ty": p.get("productType") or "",
            "img": [img(m["image"]["url"]) for m in p["media"]["nodes"] if m.get("image")],
            "opt": [{"n": o["name"], "v": o["values"]} for o in options],
            "var": variants,
        })

    active = {p["h"] for p in out_products}
    out_collections = []
    for c in collections:
        if c["handle"] == "frontpage":
            continue
        out_collections.append({
            "h": c["handle"],
            "t": c["title"],
            "d": c["descriptionHtml"],
            "p": [h for h in c["products"] if h in active],
        })

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data/catalog.json"), "w", encoding="utf-8") as f:
        json.dump({"products": out_products, "collections": out_collections}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(out_products)} products, {len(out_collections)} collections -> data/catalog.json")


if __name__ == "__main__":
    main()
