# 中国财报字段核对 · cn-financial-reconcile

把渠道金额与原文整理值放在同一口径下核对，区分数值差异、舍入差异和不可比项。

## 先看结果，再试一次

[实际生成的教学HTML预览（下载后打开）](examples/readme-preview.html) · [对应输入](examples/demo.json) · [生成与版本记录](examples/readme-preview-manifest.json)

教学样本展示金额差异、舍入核对和未核原页状态。数值匹配不等于来源已认证，教学数据不附真实PDF。 预览生成于2026-10-09，尚未取得截图或完成浏览器视觉验收；不是已发布版本的验收证明。

在仓库根目录运行，Python 3.10+，此教学demo只用标准库、不联网：

```bash
python -m cnreconcile examples/demo.json --format html --out local-data/report.html
```

打开 `local-data/report.html`。输出目录/文件须不存在；重复运行请换新路径，不覆盖旧结果。限定PDF接口需要另装可选依赖，下面的教学demo不需要。

[返回主包按问题导航](https://github.com/KILING-TASI/research-workbench/blob/codex/bounded-research-extensions/references/tool-navigation.md)；本工具可单独使用，不强制安装主包。

将财务渠道值与原文提取值配对，先核主体、期间、合并范围、币种和口径，再计算金额差异与声明精度下的舍入容差。原页证据状态单列，不把数值相同当作原文已认证。

独立项目，不依赖research-workbench。Python 3.10+，金额核对只用标准库，使用Decimal避免把浮点差误当数据冲突。

## 版本状态

更新日期：2026-10-09。公开发布为 `v0.1.0`（研究预览版）；当前分支为 `0.2.0.dev1`，增量尚未发布，不能用旧发布包调用新接口。

基础教学示例与当前开发接口分开：先运行下面的离线示例；限定原文适配、真实样本和未完成项见[开发路线](ROADMAP.md)。原始报告不随源码分发。

## 运行

```bash
python -m cnreconcile examples/demo.json
python -m cnreconcile examples/demo.json --format markdown
python -m cnreconcile examples/demo.json --format html --out local-data/review.html
python -m unittest discover -s tests -v
```

示例是人为教学数据，没有真实PDF。也可 `python -m pip install .`。输出文件须为新文件，不覆盖旧底稿。

## 输入与结果

[examples/demo.json](examples/demo.json) 包含 `asOf` 和 `pairs`。每对是reported渠道事实与extracted原文提取事实；两者都需要entity、metric、period、publishedAt、scope、currency、basis、source、value、unit。

支持金额单位元、千元、万元、亿元。`roundingUnit`是显示精度在原单位中的最小增量，不是允许任意偏差：如亿元保留两位小数可声明0.01；未声明则不额外容忍差额。总容差为两值各自半个舍入单位之和。调用者须确认实际是四舍五入显示，不能把截断精度套用该规则。

输出分为数值匹配、数值冲突和口径不可比。合并与母公司、累计与单季、不同币种不能静默比较。源数据追溯重述、更正版本、会计政策适用性仍由使用者确认；本版不自动裁定优先版本。首批开发补充支持明确原表行列的少量金额提取，以及有公告依据的更正/重述关系登记；不会自动替换旧事实，具体接口见ROADMAP.md。

可选`evidence`包含PDF物理page、quote和pdfPath。只有声明页码引句时显示“未核原页”；提供本地PDF才尝试原页检查。额外安装读取组件：

```bash
python -m pip install "pypdf>=4,<7"
```

缺组件、扫描件无法提取或找不到引句均保留未核状态，不能算通过。原页找到文字只证明引句存在，不能证明数字由该句正确提取。PDF与数据只在本地读取，不上传。

## 当前不做

不自动采集三表，不自动对任意PDF抽取字段，不提供OCR、会计准则合规意见或审计结论，不将差异直接判定造假。首版只处理已整理的金额字段，不处理每股收益、比率、货币换算及预测。

中文HTML为轻量文字报告，JSON保留基础金额、差额、容差、冲突口径、来源和页证据状态。可作为 [research-workbench](https://github.com/KILING-TASI/research-workbench) 中公司研究的独立核对环节；当前接口需明确转换，不会默认读取作者研究目录。

## 验证与许可

已本地验证单位换算、声明舍入、口径冲突、未来披露拒绝、缺证据和输出不覆盖。CI覆盖Linux/Windows、Python 3.10/3.12；核心测试不需要PDF库，不代表所有原文版式通过。

原创代码与说明使用MIT，见 [LICENSE](LICENSE)。不附第三方公告、研报、数据许可或私人样本；外部组件保留其自身许可。

## 免责声明

本项目仅供学习与研究，不构成投资建议或交易指令，不保证收益或结果准确性。请在使用前阅读[免责声明与使用边界](DISCLAIMER.md)，并结合本次数据来源、假设与缺口独立判断。代码许可不包含第三方数据使用授权。


## 后续与项目关系

已有能力、限定适配、转换契约和验收缺口见[开发路线](ROADMAP.md)。适配和定位代码已实现，限定真实样本结果见路线链接；真实更正/重述样本及其他财报版式等缺口仍保留，不代表全部已完成。

开发分支版本为`0.2.0.dev1`，此前公开发布仍是`v0.1.0`；本批功能待PR审阅，不将本地完成写成已发布。

## 许可范围

[MIT原创许可](LICENSE)（KILING-TASI及原有贡献者版权） · [第三方、示例与数据范围](THIRD_PARTY_NOTICES.md)。第三方保留原许可；代码许可不包含原文、数据或品牌的再分发授权。

## 结果表筛选与排序（待审）

当前HTML可筛选表内文字、按首列名称排序，保存输入及方法摘要。只改变显示，不重新计算或改动未知余额/口径状态；仍需新输出路径，分享前检查保存的输入。原教学预览保持冻结，本次交互未截图、未做浏览器视觉验收。

[本次实际生成的筛选排序HTML](examples/filter-sort-preview.html)沿用[教学输入](examples/demo.json)，保存输入和方法摘要；只做文本与结构检查，未截图/视觉验收。旧readme-preview.html保持冻结。

截图重试记录（2026-10-09）：用户恢复权限后，本地HTML仍被浏览器file协议策略拒绝，且禁止绕过。实际HTML生成与代码验证已完成，三个报告尚未取得浏览器截图或视觉验收；不是合成图替代，也不是许可证或原件核验通过证明。

[方法卡与教学反例](METHODS.md)说明哪些声明被校验、哪些仍需原文；本轮验证规则升级到v2，无schema旧输入仍受理，不自动迁移未知版本。


新增开发入口：[分红可持续性观察](DIVIDEND_OBSERVATION.md)，仅教学样本验收，不预测未来分红。


当前待审增量的实现、真实样本、版本与未完成项见[详细交付状态](DIVIDEND_OBSERVATION.md)；CI不代表原件认证或投资有效，不自动更新已安装版。

## 单仓隔离安装验收（当前待审版）

2026-10-10：仅本仓git源码归档构建wheel，在新目录、新venv且清除作者路径/缓存环境后，用已安装包生成教学HTML与JSON；未安装主工作台或其他自家库。模块origin位于新venv，报告教学标记、数值/未知状态与版本核对通过；重复输出拒绝，缺PDF组件不作为原页通过。CI新增同仓导出安装检查。宿主仍有其他仓库，此为目录/进程隔离，不是全新操作系统；已发布v0.1.0未另验，视觉/自然语言发现未验。
