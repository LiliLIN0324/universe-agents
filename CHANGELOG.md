# 更新记录

## 0.1.1 — 2026-11-01

对上 Qoder 实际读的字段，把「规则写在纸上」变成「规则真的生效」。

- 18 份角色卡的 `description` 补上触发语（Qoder 只按 description 认活），原来写在 `triggers` 里的词平台不读
- `sinks_to` 改为 Qoder 认识的 `skills` 字段，角色才会真的预载对应技能
- 18 席全部补 `tools` 白名单；9 个实现类角色加 `isolation: worktree`。负责人、测试、设计不再随手改代码
- 触发词重切：并发 / 上线 / 排期 / 权限 / 性能 / 选型 六组撞车全部拆开，由脚本保证全局唯一
- 新增 `team.json` 单一事实源与 `scripts/gen.py`：三张表、18 份 frontmatter、manifest 一起生成，`--check` 可挂 CI
- `plugin.json` 去掉规范里没有的 `logo`，补 `license` / `repository` / `homepage`
- README 补 `qodercli plugins validate` 与命令行装法；新增装完自检与会诊示例
- `api-contract` 的技能名前缀与其他 14 项对齐

## 0.1.0 — 2026-11-01

第一版。

- 十八席角色卡：负责人、产品、前端/后端组长、Java / Python / Go / .NET / C++、React / Vue / 跨端、UI、测试、运维、硬件组长、硬件、嵌入式
- 派活与会诊规则：单主责、跨域才会诊、结论只出一份、交接带清单
- 十五项随包技能：派活、接口契约、设计图、可编辑流程图、交互看板、效果图、高保真原型、产品与交互设计、质量门禁、测试用例、流水线、运维、全栈工程、网络拓扑、硬件与嵌入式
- Apache-2.0 授权；角色、规则与技能正文均为原创