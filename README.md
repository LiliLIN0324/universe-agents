# 宇宙智能体

[![version](https://img.shields.io/badge/version-0.1.0-blue)](CHANGELOG.md)
[![license](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

一支 18 人的虚拟交付团队，装进 Qoder 就能开始派活。

你说「这个表单要能批量导入」，它自动找到做这件事的人；你说「下周要上线，先看看有没有坑」，它会把测试、运维、后端一起叫来，各自说一段，最后负责人给结论。

这套东西来自幕景宇宙。同一工作室的开源作品还有 [Mimi](https://github.com/endtree-FDE/mimi-agent)——那是一个跑在你自己电脑上的飞书群助手。两个是同一系列：Mimi 帮你守群、记事、排日程；宇宙智能体帮你想清楚一件工程活该怎么落地。

## 谁适合用

- 一个人或小团队在做产品，缺的是「多问几个人」的那种互相挑刺
- 想让 AI 先分出「这是谁的话」：设计就谈设计，运维就谈运维，别所有岗位都用同一种腔调回答
- 手上已经有 Qoder，想要一支能直接用的团队，而不是自己一个个写角色
- 接受一句话：**它不会替你决定要不要做，只会把做这件事的代价讲清楚**

## 十八席

| 岗位 | 名字 | 什么时候找它 |
| --- | --- | --- |
| 负责人 / 主理人 | 江砚 | 取舍、拍板、要一句话结论 |
| 产品策划 | 苏禾 | 想法还糊着，先问清楚做成什么样 |
| 前端组长 | 林序 | 前端怎么分层、选什么框架、排期 |
| 后端组长 | 陆屿 | 服务怎么拆、接口怎么定 |
| Java 后端 | 顾岩 | Spring Boot 企业系统 |
| Python 后端 | 周野 | FastAPI、数据处理、自动化 |
| Go 后端 | 唐舟 | 高并发、网关、命令行工具 |
| .NET 后端 | 高铭 | ASP.NET Core、内网系统 |
| C/C++ 工程师 | 沈砺 | 性能、系统编程、内存与并发 |
| React 前端 | 白露 | React 应用与工程化 |
| Vue 前端 | 温榆 | Vue 3 中后台、表单与表格 |
| 跨端前端 | 许遥 | 小程序、uni-app、多端适配 |
| UI 设计师 | 秦时 | 交互、视觉规范、设计系统 |
| 测试工程师 | 齐澜 | 用例、自动化、放行门槛 |
| 运维工程师 | 常青 | 部署、监控、容量、回滚 |
| 硬件组长 | 骆川 | 硬件架构与软硬接口 |
| 硬件工程师 | 蒲岸 | 电路、器件、PCB、BOM |
| 嵌入式工程师 | 邵峰 | 固件、驱动、实时性 |

## 怎么装

**方式一：装压缩包（推荐）**

1. 到本仓库的 **Releases** 里下载 `universe-agents-0.1.0.zip`（这个包解开就是插件本体，没有多余的文件夹层级）
2. 打开 Qoder 的插件面板，选「安装本地插件」，选中刚下载的 zip
3. 重启 Qoder，插件列表里出现「宇宙智能体」

不要用 GitHub 的 **Code → Download ZIP**：那种包外面多套了一层 `universe-agents-main/`，安装器可能认不出插件配置。

**方式二：手动放进去（不装 zip 时用）**

把仓库内容解压到：

```
C:\Users\<你的用户名>\.qoder\plugins\cache\qoder-marketplace\universe-agents\0.1.0\
```

再在 `C:\Users\<你的用户名>\.qoder\plugins\installed_plugins_v2.json` 的 `plugins` 里加一条：

```json
"universe-agents@qoder-marketplace": [
  {
    "displayName": "宇宙智能体",
    "installPath": "<上面那个目录的完整路径>",
    "installedAt": "2026-11-01T00:00:00Z",
    "scope": "user",
    "version": "0.1.0"
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

想让某个人专门答，直接点名：「让齐澜看看这个用例够不够」。

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

## 关于原创

这套角色的名字、人设、派活规则和技能正文，都是幕景宇宙重写的。我们没有复制任何第三方插件的文本。

角色可以改。你完全可以按自己的业务把某一席换掉——建议只换岗位和一句话，不要改 `agents/` 下的文件名，免得引用断掉。

## English

A team of 18 virtual specialists that plugs into Qoder. Describe a task in plain language; it finds the right specialist, and when a task crosses roles it convenes a short consultation that ends with one written decision from the lead.

Roles cover product, front-end leads and engineers (React / Vue / cross-platform), back-end leads and engineers (Java / Python / Go / .NET), systems C/C++, UI, QA, ops, hardware and embedded. Fifteen bundled skills include dispatch, API contracts, diagrams (mermaid and editable drawio), canvas dashboards, concept images, high-fidelity prototypes, QA gates, test cases, CI/CD, ops, network topology, and hardware/embedded work.

Roles, prose and skills are original to 幕景宇宙 (Mujing Universe); no third-party plugin text is copied. Apache-2.0.

Companion project: [Mimi](https://github.com/endtree-FDE/mimi-agent), a self-hosted Feishu group assistant.