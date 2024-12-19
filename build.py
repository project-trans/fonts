#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p "python3.withPackages (ps: with ps; [ ])"

import os
import json

weight_map = {
    "ExtraLight": 200,
    "Light": 300,
    "Regular": 400,
    "Medium": 500,
    "SemiBold": 600,
    "Bold": 700,
    "Heavy": 900,
}

font_map = {
    "思源宋体": {
        "name": "SourceHanSerifSC-VF",
        "path": "./source-han-serif/Variable/TTF/SourceHanSerifSC-VF.ttf",
        "type": "file",
        "weight": "100 200 300 400 500 600 700 800 900",
    },
    "更纱黑体": {"name": "SarasaUiSC", "path": "./sarasa-ui", "type": "dir"},
    "霞骛新晰黑": {
        "name": "LXGWNewXiHei",
        "path": "./LXGWNeoXiHei.ttf",
        "type": "file",
    },
    "霞骛文楷": {"name": "LXGWWenKai", "path": "./LXGWWenKai", "type": "dir"},
    "新晰黑 Code": {
        "name": "NeoXiHeiCode-Regular",
        "path": "./NeoXiHeiCode-Regular.ttf",
        "type": "file",
    },
}


def process(dir):
    paths: list[str] = []
    for item in os.scandir(dir):
        if not item.is_file() or not (
            item.name.endswith(".otf") or item.name.endswith(".ttf")
        ):
            continue
        name = item.name.split(".")[0]
        print(f"Processing {name}...")
        weight_name = name.split("-")[-1].replace("Italic", "")
        if weight_name not in weight_map:
            print(f"Unknown weight: {weight_name}")
            weight_name = "Regular"
        weight = weight_map[weight_name]
        print(f"{{ name = {name}\tweight = {weight}\n }}")
        os.system(
            f"cn-font-split -i {item.path} --font-weight {weight} --out-dir ./result/{name}"
        )
        paths.append(name)
    return paths


if __name__ == "__main__":
    path_map: dict[str, list[str]] = {}
    for name, info in font_map.items():
        if info["type"] == "file":
            os.system(
                f'cn-font-split -i {info["path"]} --font-weight "{info["weight"] if "weight" in info else "400"}" --out-dir ./result/{info["name"]}'
            )
            path_map[name] = [info["name"]]
        elif info["type"] == "dir":
            result = process(info["path"])
            path_map[name] = []
            for item in result:
                if item.find("Mono") == -1:
                    path_map[name].append(item)
                elif f"{name} Mono" in path_map:
                    path_map[f"{name} Mono"].append(item)
                else:
                    path_map[f"{name} Mono"] = [item]
    json.dump(path_map, open("./result/path_map.json", "w"), ensure_ascii=False)
