#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p "python3.withPackages (ps: with ps; [ ])"

import os

weight_map = {
    "ExtraLight": 200,
    "Light": 300,
    "Regular": 400,
    "Medium": 500,
    "SemiBold": 600,
    "Bold": 700,
    "Heavy": 900,
}

def process(dir):
    for item in os.scandir(dir):
        if not item.is_file() or not (item.name.endswith(".otf") or item.name.endswith(".ttf")):
            continue
        name = item.name.split(".")[0]
        print(f"Processing {name}...")
        weight_name = name.split("-")[-1].replace("Italic", "")
        if weight_name not in weight_map:
            print(f"Unknown weight: {weight_name}")
            weight_name = "Regular"
        weight = weight_map[weight_name]
        print(f"{{ name = {name}\tweight = {weight}\n }}")
        os.system(f"cn-font-split -i {item.path} --font-weight {weight} --out-dir ./result/{name}")

if __name__ == "__main__":
    
    # SourceHanSerif
    dir = "./source-han-serif/OTF/SimplifiedChinese"
    process(dir)

    # Sarasa UI
    dir = "./sarasa-ui"
    process(dir)

    # LXGWNeoXiHei
    os.system(f"cn-font-split -i ./LXGWNeoXiHei.ttf --font-weight 400 --out-dir ./result/LXGWNeoXiHei")

    # LXGWWenKai
    dir = "./LXGWWenKai"
    process(dir)

    # NeoXiHei-Code
    os.system(f"cn-font-split -i ./NeoXiHeiCode-Regular.ttf --font-weight 400 --out-dir ./result/NeoXiHeiCode-Regular")
