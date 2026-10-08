# 中国财报字段核对 · cn-financial-reconcile

**v0.1.0，研究预览版。** 将财务渠道值与原文提取值配对，先核主体、期间、合并范围、币种和口径，再计算金额差异与声明精度下的舍入容差。原页证据状态单列，不把数值相同当作原文已认证。

独立项目，不依赖research-workbench。Python 3.10+，金额核对只用标准库，使用Decimal避免把浮点差误当数据冲突。

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

输出分为数值匹配、数值冲突和口径不可比。合并与母公司、累计与单季、不同币种不能静默比较。源数据追溯重述、更正版本、会计政策适用性仍由使用者确认；本版不自动裁定优先版本。

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
