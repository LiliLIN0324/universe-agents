---
name: drawio
displayName: "宇宙智能体 · 可编辑图"
description: >-
  产出 .drawio 源文件，别人可以在 draw.io 或 VS Code 里接着改。
  适用于要长期维护、多人协作、要反复调整的架构图、拓扑图、泳道图、机柜图。
  用于需要可编辑源文件而不是截图的场合。
  触发词：drawio、可编辑图、流程图、拓扑图、架构图、部署图、泳道图、机柜图、导出。
descriptionEn: >-
  Produce editable .drawio sources that others can keep editing in draw.io or VS Code,
  for diagrams that live long and change often.
---

# 可编辑图

## 什么时候用这个，什么时候不用

用 .drawio：

- 这张图会改很多次
- 有别人要接着画
- 要进文档、进 wiki、进评审材料
- 需要精确对齐、成组复制

不用：

- 只要一次说明（用 Mermaid）
- 要的是最终图片、不再改（导出 PNG/SVG 即可）
- 图只是几行流程（画图比写字慢）

## 文件结构

一个最小的 .drawio 文件：

```xml
<mxfile host="app.diagrams.net">
  <diagram id="d1" name="部署图">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10" guides="1" page="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="box1" value="接入层" vertex="1" parent="1"
                style="rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#333333;">
          <mxGeometry x="40" y="40" width="160" height="60" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

要点：

- `id="0"` 和 `id="1"` 是保留的，不要复用。
- 每条边要有 `source` 和 `target`，否则移动节点时线不会跟着。
- 坐标用整数，方便对齐到 10 格的网格。

## 画之前先定网格

先决定三层：

1. **边界**：这张图里有哪些系统、哪些外部
2. **分层**：从外到内、从上到下，每层一条横线
3. **对齐**：同层节点顶端对齐，间距一致

节点宽度建议统一，只有特别长的名字才加宽。宽度参差不齐的图，读起来格外累。

## 命名与标注

- 节点名用**产品名或服务名**，不用文件名
- 技术细节放边上的标签，不要塞进节点
- 外部系统用虚线边框，和内部区分开
- 每张图右上角写一句「这张图回答什么问题」

## 交付

1. `.drawio` 源文件（这是主交付物）
2. 导出的 PNG 或 SVG（方便贴到聊天里）
3. 一句话说明：图里的颜色、形状分别代表什么

导出时选 2 倍图，避免在文档里糊掉。中文名文件在不同系统上容易出问题，文件名用英文或拼音。

## 常见错误

- **导出 PNG 当源文件交付**：以后没人能改。
- **不用 source/target 连线**：动一个节点，线全乱。
- **颜色没有含义**：读者会猜，猜错就按错的去实现。
- **一张图画了四十个节点**：拆成「总览」和「分系统」两张。