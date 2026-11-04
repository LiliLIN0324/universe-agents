# AGENTS.md — 宇宙智能体（universe-agents）

给在本仓库干活的编码 agent 的「进入即懂」文档。开工前读完，能少走一遍弯路。

## 这个项目是什么

一支 18 人的虚拟交付团队（负责人、产品、前后端各栈、UI、测试、运维、硬件），打包成 Qoder 插件。同系列开源作品是 [Mimi](https://github.com/endtree-FDE/mimi-agent)（飞书群助手）。本仓库的产物是**内容型插件**：没有运行时服务，核心资产是 Markdown 角色/技能卡 + 一个打包脚本。

## 结构地图

| 路径 | 用途 |
|---|---|
| `team.json` | **唯一事实源**：18 席的全部字段（名字、岗位、触发词、口吻、协作关系） |
| `agents/*.md` | 生成物：每席的角色卡（frontmatter 由 gen.py 写，正文手写） |
| `skills/*/SKILL.md` | 15 个技能卡，frontmatter 对齐 agentskills.io 开放规范 |
| `scripts/gen.py` | team.json → 生成 agents/*.md frontmatter、README/qoder.md 十八席表、plugin.json 的 agents 数组 |
| `scripts/pack.py` | 打 zip 安装包 + `--check` 校验包结构（manifest 位置、角色/技能数、README 包名版本一致） |
| `scripts/check_skills.py` | 校验技能 frontmatter 符合 agentskills.io 规范 |
| `.qoder-plugin/plugin.json` | 插件 manifest；`agents` 数组是生成物，别手改 |

## 铁律：生成物不许手改

`team.json` 是唯一事实源。凡是带 `<!-- gen:seats:begin -->` / `<!-- gen:seats:end -->` 标记的表、`agents/*.md` 的 frontmatter、`plugin.json` 的 `agents` 数组，**一律改 team.json 后重新生成**，不要直接编辑生成物——CI 的一致性检查会让你白改。

## 怎么校验（改完必跑，三条全过才算完）

```bash
python scripts/gen.py --check          # team.json 与生成物一致、触发词不撞车
python scripts/pack.py --check         # 包结构、manifest、README 包名/版本一致
python scripts/check_skills.py         # 技能 frontmatter 合规
```

本地没有 Python 3.12 也能跑（纯标准库），但 CI 用 3.12。

## CI 与合入闸门

- workflow：`.github/workflows/check.yml`，唯一 job `gen-check`（main push + 全部 PR 触发）。上面三条校验就是它的三步。
- main 有分支保护：必须走 PR、过 `check / gen-check`、1 次 review。**agent 只能开 PR，不得直推 main；合并权在人。**

## 改动规范

- 改人设/触发词/岗位 → 只改 `team.json`，跑 `gen.py` 重新生成，PR 里同时含 team.json 和生成物 diff。
- 新增/修改技能 → `skills/<name>/SKILL.md`，frontmatter 的 `name` 必须等于目录名、小写连字符、带 `license` 与 `metadata`；`description` 写清"什么时候用"。
- 发布 → 版本号同步三处：`plugin.json`、`README.md` 徽章、`CHANGELOG.md`，`pack.py --check` 会卡对不上。
- PR 用仓库模板（`.github/pull_request_template.md`），验证证据贴真实命令输出。

## 已知陷阱

- 触发词（`triggers`）不能跨席位撞车，`gen.py --check` 会报。
- `skills` 卡里指向的技能目录必须真实存在。
- Release zip 必须由 `pack.py` 打：GitHub「Code → Download ZIP」外面多一层目录，Qoder 安装器认不出。
- 仓库用 Apache-2.0（见 LICENSE / NOTICE / 各 SKILL.md 的 license 字段），新文件别引入不兼容许可。
