#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""team.json 是唯一事实源，本脚本把它生成到各处。

    python scripts/gen.py           # 生成 / 覆盖
    python scripts/gen.py --check   # 只校验，内容过期则退出码 1（放 CI）

生成物：
    agents/*.md            每份的 frontmatter（正文不动）
    README.md 十八席表      两行 gen 标记之间
    qoder.md  十八席表      两行 gen 标记之间
    .qoder-plugin/plugin.json 的 agents 数组

改人、改岗位、改触发词，只改 team.json，再跑一次本脚本。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAM_PATH = os.path.join(ROOT, "team.json")
AG_DIR = os.path.join(ROOT, "agents")
SK_DIR = os.path.join(ROOT, "skills")
PLUGIN = os.path.join(ROOT, ".qoder-plugin", "plugin.json")

BEGIN = "<!-- gen:seats:begin -->"
END = "<!-- gen:seats:end -->"

# Qoder 子 Agent 认的工具名；MCP 工具形如 mcp__server__tool
TOOL_NAMES = {
    "Read", "Grep", "Glob", "Edit", "Write", "Bash", "WebSearch", "WebFetch",
    "Agent", "NotebookEdit", "TodoWrite",
}

README_HEAD = ["| 岗位 | 名字 | 什么时候找它 |", "| --- | --- | --- |"]
QODER_HEAD = ["| 岗位 | 名字 | 一句话 |", "| --- | --- | --- |"]


# ---------------------------------------------------------------- 读写

def read(path):
    """统一按 \n 读，免得 CRLF 把标记匹配搞坏。"""
    with open(path, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def newline_of(path):
    with open(path, "rb") as f:
        return "\r\n" if b"\r\n" in f.read() else "\n"


def write(path, text, nl):
    """按目标文件原有的换行风格写回，避免整文件 diff。"""
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text if nl == "\n" else text.replace("\n", nl))



# ---------------------------------------------------------------- 渲染

def description(seat):
    return "%s；%s。当用户提到%s时使用。" % (
        seat["title"], seat["core"], "、".join(seat["triggers"]))


def frontmatter(seat):
    out = [
        "---",
        "role_id: %s" % seat["id"],
        "name: %s" % seat["name"],
        "description: %s" % description(seat),
        "title: %s" % seat["title"],
        "stack: [%s]" % ", ".join(seat["stack"]),
        "expertise: [%s]" % ", ".join(seat["expertise"]),
        "collaborates: [%s]" % ", ".join(seat["collaborates"]),
        "skills: [%s]" % ", ".join(seat["skills"]),
        "tools: [%s]" % ", ".join(seat["tools"]),
    ]
    if seat.get("isolation"):
        out.append("isolation: %s" % seat["isolation"])
    out += [
        "tone: %s" % seat["tone"],
        "guardrails: [%s]" % ", ".join(seat["guardrails"]),
        "---",
        "",
    ]
    return "\n".join(out)


def table(seats, head, field):
    rows = [head[0], head[1]]
    for s in seats:
        rows.append("| %s | %s | %s |" % (s["title"], s["name"], s[field]))
    return "\n".join(rows)


def splice_block(text, block, where):
    pattern = re.compile(re.escape(BEGIN) + r"\n.*?\n" + re.escape(END), re.S)
    if not pattern.search(text):
        raise SystemExit("%s 里找不到 gen 标记（%s / %s）" % (where, BEGIN, END))
    return pattern.sub(lambda _: BEGIN + "\n" + block + "\n" + END, text, count=1)


# ---------------------------------------------------------------- 校验

def validate(seats):
    errs = []
    ids, names, triggers = set(), set(), {}
    for s in seats:
        for key in ("id", "name", "title", "core", "when", "tone"):
            if not s.get(key):
                errs.append("%s 缺字段 %s" % (s.get("id", "?"), key))
        if s["id"] in ids:
            errs.append("id 重复：%s" % s["id"])
        ids.add(s["id"])
        if s["name"] in names:
            errs.append("名字重复：%s" % s["name"])
        names.add(s["name"])
        for w in s["triggers"]:
            if w in triggers:
                errs.append("触发词撞车：「%s」同时属于 %s 和 %s（Qoder 只按 description 匹配，撞车就派错人）"
                            % (w, triggers[w], s["id"]))
            triggers[w] = s["id"]
        for sk in s["skills"]:
            if not os.path.isfile(os.path.join(SK_DIR, sk, "SKILL.md")):
                errs.append("%s 指向不存在的技能：%s" % (s["id"], sk))
        for c in s["collaborates"]:
            if c == s["id"]:
                errs.append("%s 把自己写进了 collaborates" % s["id"])
            elif c not in ids and c not in {x["id"] for x in seats}:
                errs.append("%s 的 collaborates 指向不存在的席位：%s" % (s["id"], c))
        for t in s["tools"]:
            if t not in TOOL_NAMES and not t.startswith("mcp__"):
                errs.append("%s 的工具名不在 Qoder 已知列表里：%s" % (s["id"], t))
        if not s["tools"]:
            errs.append("%s 没声明 tools，等于放开全部工具" % s["id"])
    return errs


# ---------------------------------------------------------------- 主流程

def build():
    team = json.loads(read(TEAM_PATH))
    seats = team["seats"]
    errs = validate(seats)
    if errs:
        print("校验没过，先改 team.json：")
        for e in errs:
            print("  - " + e)
        raise SystemExit(1)

    outputs = {}

    for s in seats:
        path = os.path.join(AG_DIR, s["id"] + ".md")
        old = read(path)
        m = re.match(r"^---\r?\n.*?\r?\n---\r?\n", old, re.S)
        if not m:
            raise SystemExit("%s 没有 frontmatter" % path)
        outputs[path] = frontmatter(s) + old[m.end():]

    for name, head, field in (("README.md", README_HEAD, "when"),
                              ("qoder.md", QODER_HEAD, "core")):
        path = os.path.join(ROOT, name)
        old = read(path)
        outputs[path] = splice_block(old, table(seats, head, field), name)

    plugin = json.loads(read(PLUGIN))
    plugin["agents"] = ["./agents/%s.md" % s["id"] for s in seats]
    outputs[PLUGIN] = json.dumps(plugin, ensure_ascii=False, indent=2) + "\n"

    return outputs, seats


def main():
    check = "--check" in sys.argv
    outputs, seats = build()
    stale, warns = [], []

    for path, text in outputs.items():
        old = read(path)
        if old == text:
            continue
        if check:
            stale.append(os.path.relpath(path, ROOT).replace("\\", "/"))
        else:
            write(path, text, newline_of(path))

    # 正文里的一级标题带名字，改名后容易漏
    for s in seats:
        body = read(os.path.join(AG_DIR, s["id"] + ".md"))
        if ("# %s · " % s["name"]) not in body:
            warns.append("agents/%s.md 正文标题没写「# %s · …」，改名后记得同步" % (s["id"], s["name"]))

    for w in warns:
        print("提醒：" + w)

    if check:
        if stale:
            print("以下文件与 team.json 不一致，跑一次 python scripts/gen.py：")
            for p in stale:
                print("  - " + p)
            raise SystemExit(1)
        print("team.json 与生成物一致（%d 席）。" % len(seats))
    else:
        print("已生成 %d 席：%s" % (len(seats), "、".join(s["name"] for s in seats)))


if __name__ == "__main__":
    main()
