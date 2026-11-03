#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 skills/*/SKILL.md 是否符合 Agent Skills 开放规范。

规范：https://agentskills.io/specification

    python scripts/check_skills.py            # 校验本仓库
    python scripts/check_skills.py <根目录>   # 校验别的仓库根目录

只用标准库，不依赖 PyYAML。frontmatter 只认本仓库实际使用的这几种形状：
普通标量、单/双引号标量、`>` 与 `|` 块标量、`metadata` 下面一层的字符串映射；
遇到别的写法（序列、锚点、标签、Tab 缩进、块标量里的空行、多文档、更深的嵌套、
引号不闭合、键重复、标量后还跟缩进行）直接报错退出，不猜、不静默跳过。

规范项（ERROR，会让退出码变成 1）：
  * skills/<目录>/SKILL.md 存在，且是 `---` 包起来的 frontmatter + Markdown 正文
  * name 必填：≤64 字符，只有小写字母、数字、连字符，首尾不能是连字符，必须等于目录名
  * description 必填：非空，≤1024 字符
  * license 可选；compatibility 可选，≤500 字符
  * metadata 可选，必须是「字符串 → 字符串」的一层映射
  * allowed-tools 可选，必须是空格分隔的字符串

本仓库自律项（也是 ERROR，规范没要求，但本仓库承诺了）：
  * license 必须是 Apache-2.0（插件整体 Apache-2.0）
  * metadata 必须带 author 与 version

软性项（WARN，只提醒，不影响退出码）：
  * 正文建议 ≤500 行（规范原文是 recommended，不是 must）
  * description 建议带一句明确的「什么时候用」
  * frontmatter 里出现了本仓库不认识的键（规范容忍宿主扩展）
"""
import os
import re
import sys

# ---------------------------------------------------------------- 规范常量

NAME_MAX = 64
DESC_MAX = 1024
COMPAT_MAX = 500
BODY_SOFT_MAX = 500

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
KEY_RE = re.compile(r"^([A-Za-z0-9_.\-]+):(.*)$")

SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
HOST_KEYS = {"displayName", "descriptionEn"}  # Qoder 宿主扩展，规范容忍
BLOB_INDICATORS = {">", ">-", ">+", "|", "|-", "|+"}
WHEN_MARKERS = ("当", "用于", "Use when", "use when", "Use this")
REPO_LICENSE = "Apache-2.0"
REPO_META_REQUIRED = ("author", "version")


class SkillError(Exception):
    """frontmatter 或正文的写法超出本校验器支持的范围。"""


# ---------------------------------------------------------------- 读取

def read_text(path):
    """读成 \n 结尾的文本，同时返回原始换行风格。"""
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise SkillError("文件带 UTF-8 BOM，frontmatter 必须从第一个字节开始")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SkillError("不是合法的 UTF-8：%s" % exc)
    return text.replace("\r\n", "\n")


def split_frontmatter(text):
    """切出 frontmatter 行与正文行。"""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise SkillError("第 1 行不是 ---，缺 YAML frontmatter")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], lines[i + 1:]
    raise SkillError("frontmatter 没有收尾的 ---")


# ---------------------------------------------------------------- 解析

def parse_scalar(rest, key, where):
    """解析一个单行标量。"""
    if rest.startswith('"'):
        if len(rest) < 2 or not rest.endswith('"'):
            raise SkillError("%s：%s 的引号没有闭合" % (where, key))
        body = rest[1:-1]
        out, j = [], 0
        escapes = {"n": "\n", "t": "\t", '"': '"', "\\": "\\", "/": "/"}
        while j < len(body):
            ch = body[j]
            if ch == "\\":
                if j + 1 >= len(body):
                    raise SkillError("%s：%s 以反斜杠结尾" % (where, key))
                nxt = body[j + 1]
                if nxt not in escapes:
                    raise SkillError("%s：%s 里有不支持的转义 \\%s" % (where, key, nxt))
                out.append(escapes[nxt])
                j += 2
            else:
                out.append(ch)
                j += 1
        return "".join(out)
    if rest.startswith("'"):
        if len(rest) < 2 or not rest.endswith("'"):
            raise SkillError("%s：%s 的引号没有闭合" % (where, key))
        return rest[1:-1].replace("''", "'")
    if rest[:1] in ("&", "*", "!", "{", "[", "]", ",", "|", ">", "@", "`", "%"):
        raise SkillError("%s：%s 用了本校验器不支持的 YAML 写法：%r" % (where, key, rest))
    if rest == "-" or rest.startswith("- "):
        raise SkillError("%s：%s 是序列，本校验器不支持（frontmatter 里应是字符串）" % (where, key))
    if ": " in rest or rest.endswith(":"):
        raise SkillError("%s：%s 的普通标量里还有冒号，会被 YAML 当成嵌套：%r" % (where, key, rest))
    cut = rest.find(" #")
    if cut != -1:
        rest = rest[:cut].rstrip()
    if rest == "":
        raise SkillError("%s：%s 的值是空的" % (where, key))
    return rest


def fold_block(indicator, lines, key, where):
    """解析 > / | 块标量。"""
    style, chomp = indicator[0], indicator[1:]
    if not lines:
        raise SkillError("%s：%s 声明了块标量，后面没有内容" % (where, key))
    for raw in lines:
        if raw.strip() == "":
            raise SkillError("%s：%s 的块标量里有空行，本校验器不支持这种写法" % (where, key))
        if "\t" in raw:
            raise SkillError("%s：%s 的块标量里用了 Tab 缩进" % (where, key))
    base = min(len(raw) - len(raw.lstrip(" ")) for raw in lines)
    content = [raw[base:] for raw in lines]
    if style == "|":
        text = "\n".join(content)
    else:
        parts = []
        for line in content:
            if parts:
                parts.append(" ")
            parts.append(line)
        text = "".join(parts)
    if chomp == "+":
        text = text + "\n\n"
    return text.rstrip("\n") if chomp in ("-", "") else text


def parse_nested(child, key, where):
    """解析一层嵌套映射；本仓库只有 metadata 这样写。"""
    if key != "metadata":
        raise SkillError("%s：%s 下面是嵌套映射，本仓库只允许 metadata 这样写" % (where, key))
    out = {}
    indent = None
    for raw in child:
        if raw.strip() == "":
            continue
        if "\t" in raw:
            raise SkillError("%s：metadata 里用了 Tab 缩进" % where)
        cur = len(raw) - len(raw.lstrip(" "))
        if indent is None:
            indent = cur
        elif cur != indent:
            raise SkillError("%s：metadata 里的缩进不一致" % where)
        body = raw.strip()
        if body.startswith("#"):
            continue
        m = KEY_RE.match(body)
        if not m:
            raise SkillError("%s：metadata 下有一行不是「键: 值」：%r" % (where, raw))
        k, v = m.group(1), m.group(2).strip()
        if v in BLOB_INDICATORS or v == "":
            raise SkillError("%s：metadata.%s 必须是单行字符串" % (where, k))
        if k in out:
            raise SkillError("%s：metadata 里的键 %s 重复" % (where, k))
        out[k] = parse_scalar(v, "metadata.%s" % k, where)
    return out


def parse_frontmatter(fm_lines):
    """把 frontmatter 解析成 {键: 字符串 或 {键: 字符串}}。"""
    data = {}
    i, total = 0, len(fm_lines)
    while i < total:
        raw = fm_lines[i]
        lineno = i + 2  # 文件里的行号：第 1 行是 ---
        where = "第 %d 行" % lineno
        if raw.strip() == "":
            i += 1
            continue
        if raw.startswith((" ", "\t")):
            raise SkillError("%s：这行有缩进，但不属于任何上层键：%r" % (where, raw))
        if raw.lstrip().startswith("#"):
            i += 1
            continue
        m = KEY_RE.match(raw)
        if not m:
            raise SkillError("%s：不是「键: 值」：%r" % (where, raw))
        key, rest = m.group(1), m.group(2).strip()
        if key in data:
            raise SkillError("%s：键 %s 重复出现" % (where, key))
        i += 1
        child = []
        while i < total:
            nxt = fm_lines[i]
            if nxt.strip() == "":
                child.append(nxt)
                i += 1
                continue
            if nxt.startswith((" ", "\t")):
                child.append(nxt)
                i += 1
                continue
            break
        while child and child[-1].strip() == "":
            child.pop()
        if rest in BLOB_INDICATORS:
            data[key] = fold_block(rest, child, key, where)
        elif rest == "":
            data[key] = parse_nested(child, key, where) if child else ""
        else:
            if child:
                raise SkillError("%s：%s 是个标量，后面却还跟着缩进行" % (where, key))
            data[key] = parse_scalar(rest, key, where)
    return data


# ---------------------------------------------------------------- 校验

def check_skill(skills_dir, dirname):
    """校验一项技能，返回 (errors, warns, info)。"""
    errors, warns, info = [], [], {}
    path = os.path.join(skills_dir, dirname, "SKILL.md")
    rel = "skills/%s/SKILL.md" % dirname
    if not os.path.isfile(path):
        return ["%s 不存在" % rel], warns, info
    try:
        text = read_text(path)
        fm_lines, body_lines = split_frontmatter(text)
        data = parse_frontmatter(fm_lines)
    except SkillError as exc:
        return ["%s：%s" % (rel, exc)], warns, info

    # name
    name = data.get("name", "")
    info["name"] = name
    if "name" not in data:
        errors.append("%s：缺 name（规范必填）" % rel)
    elif not isinstance(name, str):
        errors.append("%s：name 必须是字符串" % rel)
    else:
        if len(name) > NAME_MAX:
            errors.append("%s：name 超过 %d 字符（实际 %d）" % (rel, NAME_MAX, len(name)))
        if not NAME_RE.match(name):
            errors.append("%s：name 只能是小写字母、数字、连字符，且首尾不能是连字符：%r"
                          % (rel, name))
        if name != dirname:
            errors.append("%s：name=%r 与目录名 %r 不一致" % (rel, name, dirname))

    # description
    desc = data.get("description", "")
    if "description" not in data:
        errors.append("%s：缺 description（规范必填）" % rel)
    elif not isinstance(desc, str):
        errors.append("%s：description 必须是字符串" % rel)
    else:
        info["desc_len"] = len(desc)
        if not desc.strip():
            errors.append("%s：description 是空的" % rel)
        elif len(desc) > DESC_MAX:
            errors.append("%s：description 超过 %d 字符（实际 %d）" % (rel, DESC_MAX, len(desc)))
        elif not any(mark in desc for mark in WHEN_MARKERS):
            warns.append("%s：description 里看不出「什么时候用」，建议补一句" % rel)

    # license（规范可选，本仓库要求 Apache-2.0）
    if "license" not in data:
        errors.append("%s：缺 license（本仓库要求 Apache-2.0）" % rel)
    elif data["license"] != REPO_LICENSE:
        errors.append("%s：license 应为 %s，实际 %r" % (rel, REPO_LICENSE, data["license"]))
    info["license"] = data.get("license", "-")

    # compatibility（可选，≤500）
    if "compatibility" in data:
        compat = data["compatibility"]
        if not isinstance(compat, str) or not compat.strip():
            errors.append("%s：compatibility 是空的" % rel)
        elif len(compat) > COMPAT_MAX:
            errors.append("%s：compatibility 超过 %d 字符（实际 %d）"
                          % (rel, COMPAT_MAX, len(compat)))
        info["compat"] = len(compat) if isinstance(compat, str) else 0
    else:
        info["compat"] = None

    # metadata（可选，string -> string，本仓库要求 author / version）
    if "metadata" in data:
        meta = data["metadata"]
        if not isinstance(meta, dict):
            errors.append("%s：metadata 必须是「键: 值」映射" % rel)
        else:
            for k, v in sorted(meta.items()):
                if not isinstance(k, str) or not isinstance(v, str):
                    errors.append("%s：metadata.%s 不是字符串" % (rel, k))
            for need in REPO_META_REQUIRED:
                if need not in meta:
                    errors.append("%s：metadata 缺 %s（本仓库要求）" % (rel, need))
            info["meta"] = sorted(meta.keys())
    else:
        errors.append("%s：缺 metadata（本仓库要求 author / version）" % rel)
        info["meta"] = []

    # allowed-tools（可选，空格分隔字符串）
    if "allowed-tools" in data:
        tools = data["allowed-tools"]
        if not isinstance(tools, str) or not tools.strip():
            errors.append("%s：allowed-tools 是空的" % rel)
        elif "," in tools:
            errors.append("%s：allowed-tools 要用空格分隔，不能用逗号：%r" % (rel, tools))
        elif tools.split() != tools.strip().split(" "):
            errors.append("%s：allowed-tools 里有连续空格或首尾空格" % rel)
        info["tools"] = len(tools.split())

    # 正文
    body = "\n".join(body_lines)
    n_body = len(body.strip("\n").split("\n")) if body.strip() else 0
    info["body"] = n_body
    if n_body == 0:
        errors.append("%s：frontmatter 之后没有正文" % rel)
    elif n_body > BODY_SOFT_MAX:
        warns.append("%s：正文 %d 行，超过建议的 %d 行；长内容应挪到 references/"
                     % (rel, n_body, BODY_SOFT_MAX))

    # 不认识的键
    unknown = sorted(set(data) - SPEC_KEYS - HOST_KEYS)
    if unknown:
        warns.append("%s：有规范外的键 %s（宿主扩展可容忍，但请确认是有意为之）"
                     % (rel, "、".join(unknown)))
    return errors, warns, info


def main(argv):
    if len(argv) > 2:
        print("用法：python scripts/check_skills.py [仓库根目录]")
        return 2
    if len(argv) == 2:
        root = os.path.abspath(argv[1])
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(root, "skills")
    if not os.path.isdir(skills_dir):
        print("找不到技能目录：%s" % skills_dir)
        return 1

    entries = sorted(os.listdir(skills_dir))
    dirs = [d for d in entries if os.path.isdir(os.path.join(skills_dir, d))]
    loose = [e for e in entries if not os.path.isdir(os.path.join(skills_dir, e))]
    if not dirs:
        print("skills/ 下面一个技能目录都没有")
        return 1

    all_errors, all_warns = [], []
    if loose:
        all_errors.append("skills/ 下面有不是目录的东西：%s" % "、".join(loose))

    for dirname in dirs:
        errors, warns, info = check_skill(skills_dir, dirname)
        all_errors += errors
        all_warns += warns
        if errors:
            print("[FAIL] %-26s %d 处不符合规范" % (dirname, len(errors)))
        else:
            print("[ OK ] %-26s name=%s  description=%d字  license=%s  compatibility=%s  "
                  "metadata=%s  正文=%d行"
                  % (dirname, info.get("name", "?"), info.get("desc_len", 0),
                     info.get("license", "-"),
                     "%d字" % info["compat"] if info.get("compat") is not None else "无",
                     ",".join(info.get("meta", [])) or "-",
                     info.get("body", 0)))

    if all_warns:
        print()
        print("提醒（不阻塞）：")
        for w in all_warns:
            print("  · " + w)
    if all_errors:
        print()
        print("不符合规范：")
        for e in all_errors:
            print("  × " + e)

    print()
    print("-" * 72)
    print("共 %d 项技能：%d 项通过，%d 项失败，%d 条提醒。"
          % (len(dirs), len(dirs) - len({e.split("：")[0] for e in all_errors}),
             len({e.split("：")[0] for e in all_errors}), len(all_warns)))
    if all_errors:
        print("不符合 Agent Skills 规范，退出码 1。")
        return 1
    print("全部符合 Agent Skills 规范。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
