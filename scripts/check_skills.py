#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 agentskills.io 开放规范校验 skills/*/SKILL.md 的 frontmatter。

用法：
    python scripts/check_skills.py

规范来源：https://agentskills.io/specification
    name          必填，1-64 字符，仅 a-z / 0-9 / 连字符，不得首尾为连字符，
                  不得出现连续连字符，且必须等于所在目录名
    description   必填，1-1024 字符，非空，需说明「做什么」与「什么时候用」
    license       选填，短字符串（本仓库策略：必填，见 REPO_ 标注）
    compatibility 选填，1-500 字符，只有确实存在环境要求时才写
    metadata      选填，string -> string 映射（本仓库策略：必填，且至少含 author / version）
    allowed-tools 选填，空格分隔的字符串（实验性）
    正文           规范建议 < 500 行

本仓库策略严于规范的部分统一用 REPO_ 前缀标注；规范里 license / metadata 是选填。

只依赖标准库。frontmatter 用一个小的 YAML 子集解析器自己解析，支持的形状仅限：
    顶层 `key: value`（纯量 / 双引号 / 单引号 / {...} 流式映射）
    折叠块 `>-` `>` 与字面块 `|-` `|`（可带 - 或 + 收尾指示符）
    一层缩进映射（`metadata:` 下面两空格缩进的 key: value）
遇到别的写法（列表、多级嵌套、锚点、tag、未知指示符等）直接报错，不静默跳过。
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")

NAME_MAX = 64
DESC_MIN = 1
DESC_MAX = 1024
COMPAT_MIN = 1
COMPAT_MAX = 500
BODY_LINE_HINT = 500

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# REPO_ 本仓库策略：license 与 metadata 属于规范选填字段，但本项目要求每个技能都写。
REPO_REQUIRED_FIELDS = ("name", "description", "license", "metadata")
REPO_REQUIRED_METADATA = ("author", "version")

# 规范字段全集；其余顶层键视为客户端扩展（容忍，只在汇总里提示）。
SPEC_FIELDS = ("name", "description", "license", "compatibility", "metadata", "allowed-tools")

# description 里「什么时候用」的提示词。规范用的是 should 而非 must，
# 所以这里只出 WARN，不影响退出码。
WHEN_HINTS = (
    "使用", "用于", "适用于", "触发词",
    "Use when", "use when", "Use for", "use for", "Use this",
)

BLOCK_HEADER_RE = re.compile(r"^(?P<style>[>|])(?P<chomp>[-+]?)$")
KEY_RE = re.compile(r"^(?P<key>[A-Za-z0-9_.\-]+):(?:[ \t](?P<rest>.*))?$")


class FrontmatterError(Exception):
    """frontmatter 不是本解析器支持的形状——报错，不猜。"""


# --------------------------------------------------------------------------
# 小型 YAML 子集解析器
# --------------------------------------------------------------------------

def _unescape_double(raw, where):
    out = []
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "\\":
            if i + 1 >= len(raw):
                raise FrontmatterError("%s 双引号字符串以反斜杠结尾" % where)
            nxt = raw[i + 1]
            mapping = {"n": "\n", "t": "\t", '"': '"', "\\": "\\", "0": "\0"}
            if nxt not in mapping:
                raise FrontmatterError("%s 双引号字符串里有不支持的转义 \\%s" % (where, nxt))
            out.append(mapping[nxt])
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _split_flow_items(raw, where):
    """把 `a: 1, b: "2"` 切成条目，逗号要避开引号里面。"""
    items = []
    buf = []
    quote = None
    i = 0
    while i < len(raw):
        ch = raw[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(raw):
                buf.append(raw[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if ch == ",":
            items.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if quote:
        raise FrontmatterError("%s 流式映射里的引号没有闭合" % where)
    items.append("".join(buf))
    return [x for x in (s.strip() for s in items) if x != ""]


def _parse_flow_map(raw, where):
    if not raw.endswith("}"):
        raise FrontmatterError("%s 流式映射 `{` 没有闭合：%r" % (where, raw))
    inner = raw[1:-1].strip()
    result = {}
    if inner == "":
        return result
    for item in _split_flow_items(inner, where):
        if ":" not in item:
            raise FrontmatterError("%s 流式映射条目不是 key: value：%r" % (where, item))
        k, _, v = item.partition(":")
        k = k.strip()
        if not k:
            raise FrontmatterError("%s 流式映射条目 key 为空：%r" % (where, item))
        if k in result:
            raise FrontmatterError("%s 流式映射 key 重复：%s" % (where, k))
        result[k] = _parse_scalar(v, where)
    return result


def _parse_scalar(raw, where):
    """解析一个行内纯量。返回 str；无法识别就报错。"""
    s = raw.strip()
    if s == "":
        return None
    if s.startswith('"'):
        if not s.endswith('"') or len(s) < 2:
            raise FrontmatterError("%s 双引号没有闭合：%r" % (where, s))
        return _unescape_double(s[1:-1], where)
    if s.startswith("'"):
        if not s.endswith("'") or len(s) < 2:
            raise FrontmatterError("%s 单引号没有闭合：%r" % (where, s))
        return s[1:-1].replace("''", "'")
    if s.startswith("{"):
        return _parse_flow_map(s, where)
    if s[0] in "[]&*!|>%@`":
        raise FrontmatterError("%s 不支持的行内写法（列表/锚点/tag/块指示符）: %r" % (where, s))
    cut = s.find(" #")
    if cut >= 0:
        s = s[:cut].rstrip()
    if ": " in s or s.endswith(":"):
        raise FrontmatterError("%s 纯量里出现 `: `，只支持单行 key: value：%r" % (where, s))
    return s


def _fold(lines, where):
    """折叠块标量：单个换行折成空格，空行折成换行。"""
    out = ""
    pending_blank = 0
    started = False
    for line in lines:
        text = line.rstrip()
        if text == "":
            pending_blank += 1
            continue
        if not started:
            out = text
            started = True
        elif pending_blank:
            out += "\n" * pending_blank + text
        else:
            out += " " + text
        pending_blank = 0
    return out


def _apply_chomp(value, chomp, where):
    if chomp == "-":
        return value.rstrip("\n")
    if chomp == "+":
        return value
    # clip（默认）：保留一个结尾换行
    return value.rstrip("\n") + "\n" if value != "" else value


def _read_block_scalar(lines, idx, header, where):
    m = BLOCK_HEADER_RE.match(header)
    assert m  # 调用方已判断
    style, chomp = m.group("style"), m.group("chomp")
    collected = []
    indent = None
    j = idx + 1
    while j < len(lines):
        line = lines[j]
        if line.strip() == "":
            collected.append("")
            j += 1
            continue
        cur = len(line) - len(line.lstrip(" "))
        if cur == 0:
            break
        if indent is None:
            indent = cur
        elif cur < indent:
            break
        collected.append(line[indent:])
        j += 1
    while collected and collected[-1] == "":
        collected.pop()
    value = _fold(collected, where) if style == ">" else "\n".join(x.rstrip() for x in collected)
    return _apply_chomp(value, chomp, where), j


def parse_frontmatter(lines, path):
    """解析 frontmatter 行（不含两侧 ---）。失败即抛 FrontmatterError。"""
    data = {}
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        lineno = i + 2  # 文件里的真实行号：第 1 行是 ---
        where = "%s 第 %d 行" % (path, lineno)
        if line.strip() == "":
            i += 1
            continue
        if line[:1] in (" ", "\t"):
            raise FrontmatterError("%s 意外缩进：顶层只接受 `key: value`：%r" % (where, line))
        m = KEY_RE.match(line)
        if not m:
            raise FrontmatterError("%s 不是 `key: value`：%r" % (where, line))
        key = m.group("key")
        rest = (m.group("rest") or "").strip()
        if key in data:
            raise FrontmatterError("%s key 重复：%s" % (where, key))

        if rest == "":
            look = i + 1
            children = []
            child_indent = None
            while look < n:
                nxt = lines[look]
                if nxt.strip() == "":
                    look += 1
                    continue
                cur = len(nxt) - len(nxt.lstrip(" "))
                if cur == 0:
                    break
                if child_indent is None:
                    child_indent = cur
                elif cur != child_indent:
                    raise FrontmatterError(
                        "%s 第 %d 行 缩进不一致（%d vs %d），只支持一层等宽缩进映射"
                        % (path, look + 2, cur, child_indent))
                children.append((look + 2, nxt.strip()))
                look += 1
            if not children:
                data[key] = None
                i += 1
                continue
            child_map = {}
            for clineno, ctext in children:
                cm = KEY_RE.match(ctext)
                if not cm:
                    raise FrontmatterError(
                        "%s 第 %d 行：映射子项不是 `key: value`：%r" % (path, clineno, ctext))
                ckey = cm.group("key")
                crestick = (cm.group("rest") or "").strip()
                if crestick == "":
                    raise FrontmatterError(
                        "%s 第 %d 行：映射值不能为空，也不支持再嵌套一层" % (path, clineno))
                if ckey in child_map:
                    raise FrontmatterError("%s 第 %d 行：映射 key 重复：%s" % (path, clineno, ckey))
                child_map[ckey] = _parse_scalar(crestick, "%s 第 %d 行" % (path, clineno))
            data[key] = child_map
            i = look
            continue

        bm = BLOCK_HEADER_RE.match(rest)
        if bm:
            value, nxt = _read_block_scalar(lines, i, rest, where)
            data[key] = value
            i = nxt
            continue
        if rest[0] in "|>":
            # 例如 `>2` / `|+2`：缩进指示符，本子集不支持
            raise FrontmatterError("%s 不支持的块标量写法：%r" % (where, rest))
        data[key] = _parse_scalar(rest, where)
        i += 1
    return data


def split_frontmatter(text, path):
    if text.startswith("\ufeff"):
        raise FrontmatterError("%s 以 UTF-8 BOM 开头，frontmatter 必须以 --- 开头" % path)
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        raise FrontmatterError("%s 第 1 行不是 frontmatter 起始的 ---" % path)
    end = None
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            end = i
            break
    if end is None:
        raise FrontmatterError("%s frontmatter 缺少结束的 --- 分隔行" % path)
    body = lines[end + 1:]
    if body and body[-1] == "":
        body = body[:-1]           # 末尾换行带来的空元素不算一行
    if body and body[0].strip() == "":
        body = body[1:]            # 分隔行后的空行不算正文第一行
    return lines[1:end], body


# --------------------------------------------------------------------------
# 校验
# --------------------------------------------------------------------------

def check_skill(dir_name, path):
    """返回 (errors, warnings, info)。errors 非空即为不合格。"""
    errors = []
    warnings = []
    info = {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return ["读不到文件：%s" % exc], [], info

    try:
        fm_lines, body = split_frontmatter(text, path)
        fm = parse_frontmatter(fm_lines, path)
    except FrontmatterError as exc:
        return ["frontmatter 解析失败：%s" % exc], [], info

    info["body_lines"] = len(body)

    # 必填字段（license / metadata 是本仓库策略，规范里选填）
    for field in REPO_REQUIRED_FIELDS:
        if field not in fm or fm[field] in (None, "", {}, []):
            tag = "" if field in ("name", "description") else "（本仓库策略，规范选填）"
            errors.append("缺少必填字段 `%s`%s" % (field, tag))

    # name
    name = fm.get("name")
    if name is not None:
        if not isinstance(name, str):
            errors.append("`name` 必须是字符串，实际是 %s" % type(name).__name__)
        else:
            if len(name) > NAME_MAX:
                errors.append("`name` 长度 %d > %d" % (len(name), NAME_MAX))
            if not NAME_RE.match(name):
                errors.append(
                    "`name` 不符合 ^[a-z0-9]+(-[a-z0-9]+)*$（小写字母/数字/连字符，"
                    "不得首尾连字符、不得连续连字符）：%r" % name)
            if name != dir_name:
                errors.append("`name` (%s) 与目录名 (%s) 不一致" % (name, dir_name))
            info["name"] = name

    # description
    desc = fm.get("description")
    if desc is not None:
        if not isinstance(desc, str):
            errors.append("`description` 必须是字符串，实际是 %s" % type(desc).__name__)
        else:
            d = desc.strip()
            if len(d) < DESC_MIN:
                errors.append("`description` 为空")
            if len(desc) > DESC_MAX:
                errors.append("`description` 长度 %d > %d" % (len(desc), DESC_MAX))
            info["desc_len"] = len(desc)
            if d and not any(h in desc for h in WHEN_HINTS):
                warnings.append(
                    "`description` 里看不出「什么时候用」（规范用 should）："
                    "建议补一句 `用于…` / `Use when…`")

    # license
    lic = fm.get("license")
    if lic is not None:
        if not isinstance(lic, str) or lic.strip() == "":
            errors.append("`license` 必须是非空字符串")
        else:
            info["license"] = lic

    # compatibility（规范：1-500 字符；本仓库策略：只有真有环境要求才写）
    compat = fm.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            errors.append("`compatibility` 必须是字符串，实际是 %s" % type(compat).__name__)
        else:
            if not (COMPAT_MIN <= len(compat) <= COMPAT_MAX):
                errors.append("`compatibility` 长度 %d 不在 %d-%d"
                              % (len(compat), COMPAT_MIN, COMPAT_MAX))
            info["compat_len"] = len(compat)

    # metadata（规范：string -> string）
    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            errors.append("`metadata` 必须是 key: value 映射，实际是 %s" % type(meta).__name__)
        else:
            for k, v in meta.items():
                if not isinstance(v, str):
                    errors.append("`metadata.%s` 的值必须是字符串" % k)
            for k in REPO_REQUIRED_METADATA:
                if k not in meta or not str(meta.get(k, "")).strip():
                    errors.append("`metadata` 缺少 `%s`（本仓库策略）" % k)
            info["meta_keys"] = ",".join(meta.keys())

    # allowed-tools（规范：空格分隔字符串，实验性）
    tools = fm.get("allowed-tools")
    if tools is not None and not isinstance(tools, str):
        errors.append("`allowed-tools` 必须是空格分隔的字符串，不是 %s" % type(tools).__name__)

    # 正文长度只是规范建议，报告但不判失败
    if info["body_lines"] > BODY_LINE_HINT:
        warnings.append("正文 %d 行 > %d 行（规范建议值，仅提示，不判失败）"
                        % (info["body_lines"], BODY_LINE_HINT))

    info["extra_fields"] = [k for k in fm.keys() if k not in SPEC_FIELDS]
    return errors, warnings, info


def main():
    if not os.path.isdir(SKILLS_DIR):
        print("找不到技能目录：%s" % SKILLS_DIR)
        return 1

    entries = sorted(
        d for d in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, d))
    )
    if not entries:
        print("技能目录为空：%s" % SKILLS_DIR)
        return 1

    print("规范来源：https://agentskills.io/specification")
    print("校验目录：%s" % SKILLS_DIR)
    print("-" * 78)

    n_pass = n_fail = n_warn = 0
    extra_seen = set()

    for dir_name in entries:
        path = os.path.join(SKILLS_DIR, dir_name, "SKILL.md")
        if not os.path.isfile(path):
            print("FAIL  %-28s 目录下没有 SKILL.md" % dir_name)
            n_fail += 1
            continue
        errors, warnings, info = check_skill(dir_name, path)
        extra_seen.update(info.get("extra_fields", []))

        if errors:
            n_fail += 1
            print("FAIL  %-28s %d 处不合规，正文 %s 行"
                  % (dir_name, len(errors), info.get("body_lines", "?")))
            for e in errors:
                print("        - %s" % e)
        else:
            n_pass += 1
            compat = info.get("compat_len")
            print("PASS  %-28s name=%s  desc=%s/%d  license=%s  metadata=[%s]  compat=%s  body=%s 行"
                  % (dir_name,
                     info.get("name", "?"),
                     info.get("desc_len", "?"), DESC_MAX,
                     info.get("license", "-"),
                     info.get("meta_keys", "-"),
                     ("%d 字符" % compat) if compat else "-",
                     info.get("body_lines", "?")))
        if warnings:
            n_warn += 1
            for w in warnings:
                print("WARN  %-28s %s" % (dir_name, w))

    print("-" * 78)
    print("技能 %d 个：通过 %d，失败 %d，带警告 %d"
          % (len(entries), n_pass, n_fail, n_warn))
    if extra_seen:
        print("提示：非规范字段（客户端扩展，容忍；不参与判定）：%s"
              % ", ".join(sorted(extra_seen)))
    if n_fail:
        print("结果：不合规（%d 个技能需要修）" % n_fail)
        return 1
    print("结果：全部符合规范")
    return 0


if __name__ == "__main__":
    sys.exit(main())
