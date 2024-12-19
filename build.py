#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p "python3.withPackages (ps: with ps; [ ])"

import json
import os
import re

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
            f"cn-font-split -i {item.path} --font-family {name.split("-")[0]} --font-weight {weight} --out-dir ./result/{name}"
        )
        paths.append(name)
    return paths


class FontMapItem:
    fontFamily: str
    paths: list[str]

    def __init__(self, paths: list[str], font_family: str):
        self.paths = paths
        self.fontFamily = font_family


class FontMapItemEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, FontMapItem):
            return o.__dict__
        return super().default(o)


if __name__ == "__main__":
    path_map: dict[str, FontMapItem] = {}
    for name, info in font_map.items():
        if info["type"] == "file":
            outdir = f'./result/{info["name"]}'
            os.system(
                f'cn-font-split -i {info["path"]} --font-weight "{info["weight"] if "weight" in info else "400"}" --out-dir {outdir}'
            )
            css = open(f"{outdir}/result.css", "r", encoding="utf-8").read()
            font_family = re.search(r"(?<=font-family:\").*(?=\";)", css).group()
            path_map[name] = FontMapItem(paths=[info["name"]], font_family=font_family)
        elif info["type"] == "dir":
            result = process(info["path"])
            for item in result:
                if item.find("Mono") == -1:
                    if name in path_map:
                        path_map[name].paths.append(item)
                    else:
                        css = open(
                            f"./result/{item}/result.css", "r", encoding="utf-8"
                        ).read()
                        font_family = re.search(
                            r"(?<=font-family:\").*(?=\";)", css
                        ).group()
                        path_map[name] = FontMapItem(
                            paths=[item], font_family=font_family
                        )
                elif f"{name} Mono" in path_map:
                    path_map[f"{name} Mono"].paths.append(item)
                else:
                    css = open(
                        f"./result/{item}/result.css", "r", encoding="utf-8"
                    ).read()
                    font_family = re.search(
                        r"(?<=font-family:\").*(?=\";)", css
                    ).group()
                    path_map[f"{name} Mono"] = FontMapItem(
                        paths=[item], font_family=font_family
                    )
    json.dump(
        path_map,
        open("./result/path_map.json", "w"),
        ensure_ascii=False,
        cls=FontMapItemEncoder,
    )
