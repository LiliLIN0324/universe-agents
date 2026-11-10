# 宇宙智能体

[![version](https://img.shields.io/badge/version-0.1.1-blue)](CHANGELOG.md)
[![license](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

一支 18 人的虚拟交付团队，装进 Qoder 就能开始派活。

你说「这个表单要能批量导入」，它自动找到做这件事的人；你说「下周要上线，先看看有没有坑」，它会把测试、运维、后端一起叫来，各自说一段，最后负责人给结论。

这套东西来自幕景宇宙。同一工作室的开源作品还有 [Mimi](https://github.com/endtree-FDE/mimi-agent)——那是一个跑在你自己电脑上的飞书群助手。两个是同一系列：Mimi 帮你守群、记事、排日程，写操作走决策门禁与双人复核；宇宙智能体帮你想清楚一件工程活该怎么落地。

## 谁适合用

- 一个人或小团队在做产品，缺的是「多问几个人」的那种互相挑刺
- 想让 AI 先分出「这是谁的话」：设计就谈设计，运维就谈运维，别所有岗位都用同一种腔调回答
- 手上已经有 Qoder，想要一支能直接用的团队，而不是自己一个个写角色
- 接受一句话：**它不会替你决定要不要做，只会把做这件事的代价讲清楚**

## 十八席

<!-- gen:seats:begin -->
| 岗位 | 名字 | 什么时候找它 |
| --- | --- | --- |
| 负责人 / 主理人 | 江砚 | 取舍、拍板、要一句话结论 |
| 产品策划 | 苏禾 | 想法还糊着，先问清楚做成什么样 |
| 前端组长 | 林序 | 前端怎么分层、选什么框架、排期 |
| 后端组长 | 陆屿 | 服务怎么拆、接口怎么定 |
| Java 后端工程师 | 顾岩 | Spring Boot 企业系统 |
| Python 后端工程师 | 周野 | FastAPI、数据处理、自动化 |
| Go 后端工程师 | 唐舟 | 高并发、网关、命令行工具 |
| .NET 后端工程师 | 高铭 | ASP.NET Core、内网系统 |
| C/C++ 工程师 | 沈砺 | 性能、系统编程、内存与并发 |
| React 前端工程师 | 白露 | React 应用与工程化 |
| Vue 前端工程师 | 温榆 | Vue 3 中后台、表单与表格 |
| 跨端前端工程师 | 许遥 | 小程序、uni-app、多端适配 |
| UI 设计师 | 秦时 | 交互、视觉规范、设计系统 |
| 测试工程师 | 齐澜 | 用例、自动化、放行门槛 |
| 运维工程师 | 常青 | 部署、监控、容量、回滚 |
| 硬件组组长 | 骆川 | 硬件架构与软硬接口 |
| 硬件工程师 | 蒲岸 | 电路、器件、PCB、BOM |
| 嵌入式开发工程师 | 邵峰 | 固件、驱动、实时性 |
<!-- gen:seats:end -->

## 怎么装

**方式一：装压缩包（推荐）**

1. 到本仓库的 **Releases** 里下载 `universe-agents-0.1.1.zip`（这个包解开就是插件本体，没有多余的文件夹层级）
2. 打开 Qoder 的插件面板，选「安装本地插件」，选中刚下载的 zip
3. 重启 Qoder，插件列表里出现「宇宙智能体」

不要用 GitHub 的 **Code → Download ZIP**：那种包外面多套了一层 `universe-agents-main/`，安装器可能认不出插件配置。

**方式二：命令行装（zip 装不上时用）**

Qoder CLI 装本地插件认的是**目录**，不是 zip。解压后指到目录即可：

```
qodercli plugins install <解压出来的目录>
qodercli plugins reload
```

装之前先让 CLI 自己检查一遍结构：

```
qodercli plugins validate <解压出来的目录>
```

它会把发现的 18 个 Agent 和 15 个 Skill 列出来；列不全就是包不对。

**方式三：手动放进去（不走安装器时用）**

把仓库内容解压到：

```
C:\Users\<你的用户名>\.qoder\plugins\cache\qoder-marketplace\universe-agents\0.1.1\
```

再在 `C:\Users\<你的用户名>\.qoder\plugins\installed_plugins_v2.json` 的 `plugins` 里加一条：

```json
"universe-agents@qoder-marketplace": [
  {
    "displayName": "宇宙智能体",
    "installPath": "<上面那个目录的完整路径>",
    "installedAt": "2026-11-01T00:00:00Z",
    "scope": "user",
    "version": "0.1.1"
  }
]
```

改这个文件之前先复制一份备份。JSON 少一个逗号，Qoder 会读不出所有插件。

## 怎么派活

直接说人话就行，不用背岗位名：

- 「这个活动报名表要能批量导入 Excel，下周要用」——会自动落到苏禾 → 温榆 → 齐澜
- 「上线前帮我过一遍」——测试、运维、主责后端一起看，江砚给结论
- 「这个接口设计对不对」——陆屿主答，涉及具体语言时叫对应的人
- 「我想先看看做出来是什么样」——秦时出交互，林序评估工期

想让某个人专门答，直接点名：「让齐澜看看这个用例够不够」。这是最稳的用法——Qoder 按每个角色的 `description` 认活，点名就绕过了猜测。

### 装完先自检

1. 问「让齐澜看看这个交付能不能放行」——回话该是测试口吻：测了什么、不测什么、通过/失败/未测各几条。
2. 问「这两个功能下周只能上一个，选哪个」——该是江砚给结论，且必须写出**放弃了什么**。
3. 两次都变成同一段通用建议，就是插件没加载：跑 `qodercli plugins list` 看「宇宙智能体」在不在。

### 一次会诊长什么样

下面是按团队规则该有的形态（示例，不是真实会话截图）：

```
你：下周三要上线，先看看有没有坑。

常青（运维）：回滚脚本上一版没跑过，这次得先在预发验一遍；
  现在只有接口耗时监控，没有错误率，出事只能等用户报。
齐澜（测试）：这版动了订单接口的返回结构，回归范围是下单、退款、对账三条链路；
  对账目前只走了正常路径，异常未覆盖。
陆屿（后端组长）：多返回两个字段属于新增，不破坏兼容；
  但退款服务还在读老字段，联调前要给个切换窗口。
江砚（负责人）：结论——周三只发订单接口，退款服务押到下周三。
  理由：新增字段不破坏兼容，退款跨两个服务，来不及回归。
  代价：退款要等一周，客服会有问询。回看：下周三退款没进预发就砍掉。
```

最后那段是关键：**选了什么、放弃了什么、什么时候回头看**，三样缺一就不算结论。

## 十八席怎么协作

```mermaid
flowchart LR
  ask["你说一句话"] --> route["认活：这件事谁主责"]
  route --> one["单岗位直接答"]
  route --> consult["跨岗位会诊：各说本段"]
  consult --> call["江砚写结论：选了什么 / 放弃什么 / 何时回头看"]
  one --> hand["交接清单：状态 / 下一步 / 缺什么 / 谁在等"]
  call --> hand
```

三条底线写死在团队里：**不替别人承诺**、**交接不带口头约定**、**说不出证据就不算完成**。

## 随包技能（15 项）

派活（delivery-team）、接口契约（api-contract）、设计图（design-diagrams）、可编辑流程图（drawio）、交互看板（canvas-studio）、效果图（effect-image）、高保真原型（high-fidelity-prototype）、产品与交互设计（product-design）、质量门禁（qa-quality）、测试用例（test-case）、流水线（devops-pipeline）、运维专家（ops-expert）、全栈工程（fullstack-engineering）、网络拓扑（network-topology）、硬件与嵌入式（hardware-embedded）。

技能随插件打包，不依赖你本机另外装过什么。

## 改这支团队

`team.json` 是唯一事实源：名字、岗位、一句话、触发词、工具边界、协作对象、对应技能都在里面。改完跑：

```
python scripts/gen.py          # 重新生成
python scripts/gen.py --check  # 只检查，过期返回非 0，可挂 CI
```

它会生成四处：18 份 `agents/*.md` 的 frontmatter、README 与 `qoder.md` 的十八席表、`plugin.json` 的 agents 数组。正文不生成，随手改。

两条硬约束由脚本把关：**触发词全局唯一**（Qoder 只按 `description` 匹配，两个角色抢同一个词就会派错人）、**`skills` 指向的技能目录必须存在**。

想加一个人：在 `team.json` 里加一条，`id` 就是 `agents/<id>.md` 的文件名。

## 关于原创

这套角色的名字、人设、派活规则和技能正文，都是幕景宇宙重写的。我们没有复制任何第三方插件的文本。

角色可以改。你完全可以按自己的业务把某一席换掉，见下一节。

## English

A team of 18 virtual specialists that plugs into Qoder. Describe a task in plain language; it finds the right specialist, and when a task crosses roles it convenes a short consultation that ends with one written decision from the lead.

Roles cover product, front-end leads and engineers (React / Vue / cross-platform), back-end leads and engineers (Java / Python / Go / .NET), systems C/C++, UI, QA, ops, hardware and embedded. Fifteen bundled skills include dispatch, API contracts, diagrams (mermaid and editable drawio), canvas dashboards, concept images, high-fidelity prototypes, QA gates, test cases, CI/CD, ops, network topology, and hardware/embedded work.

Roles, prose and skills are original to 幕景宇宙 (Mujing Universe); no third-party plugin text is copied. Apache-2.0.

Companion project: [Mimi](https://github.com/endtree-FDE/mimi-agent), a self-hosted Feishu group assistant.