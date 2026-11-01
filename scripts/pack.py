#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打安装包：dist/universe-agents-<version>.zip

    python scripts/pack.py           # 打包（版本号从 plugin.json 读）
    python scripts/pack.py --check   # 只校验结构与 README 里的包名

包解开就是插件本体，顶层直接是 .qoder-plugin/、agents/、skills/，不多套一层。
.github/、dist/、.gitignore 不进包。
"""
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", ".github", "dist", "__pycache__", ".idea", ".vscode"}
SKIP_FILES = {".gitignore", ".DS_Store", "Thumbs.db"}
SKILL_TOTAL = 15


def collect():
    names = []
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(fs):
            rel = os.path.relpath(os.path.join(d, f), ROOT).replace("\\", "/")
            if rel in SKIP_FILES or rel.endswith((".zip", ".patch")):
                continue
            names.append(rel)
    return sorted(names)


def main():
    check = "--check" in sys.argv
    with open(os.path.join(ROOT, ".qoder-plugin", "plugin.json"), encoding="utf-8") as f:
        plugin = json.load(f)
    version = plugin["version"]
    names = collect()

    errs = []
    if ".qoder-plugin/plugin.json" not in names:
        errs.append("包里没有 .qoder-plugin/plugin.json，安装器认不出")
    n_agents = len([n for n in names if n.startswith("agents/") and n.endswith(".md")])
    n_skills = len([n for n in names if n.startswith("skills/") and n.endswith("/SKILL.md")])
    if n_agents != len(plugin["agents"]):
        errs.append("包里 %d 个角色，manifest 声明 %d 个" % (n_agents, len(plugin["agents"])))
    if n_skills != SKILL_TOTAL:
        errs.append("包里 %d 个技能，应为 %d 个" % (n_skills, SKILL_TOTAL))
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        readme = f.read()
    want = "universe-agents-%s.zip" % version
    if want not in readme:
        errs.append("README 里没提 %s，版本号和文档对不上" % want)
    if errs:
        print("包结构有问题：")
        for e in errs:
            print("  - " + e)
        raise SystemExit(1)

    if check:
        print("包结构 OK：%d 个文件｜%d 角色｜%d 技能｜版本 %s"
              % (len(names), n_agents, n_skills, version))
        return

    out_dir = os.path.join(ROOT, "dist")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, want)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in names:
            z.write(os.path.join(ROOT, rel), rel)
    print("打好 %s：%d 个文件，%.0f KB"
          % (os.path.relpath(out, ROOT), len(names), os.path.getsize(out) / 1024.0))


if __name__ == "__main__":
    main()
