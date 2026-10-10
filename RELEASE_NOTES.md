# v0.2.0 发布说明

本版把已在main集成的财报金额核对、指定原表位置检查、选定更正前后字段对照与分红观察打包到同一版本。软件版本为0.2.0；已有输入schema、金额规则和分红方法版本保持，不改历史报告。

保存报告后提示结果位置及打开文件；失败给出换新输出名、核对输入或安装可选PDF组件的下一步。说明走stderr，默认JSON和Python函数返回键保持兼容。

## 下载与安装

v0.2.0已于2026-10-10发布，三个包从main提交`88304c16b42c9864c9e20a7383b55b5250e179bd`重建并验收；GitHub资产摘要与本地最终包一致。此前候选与历史报告保留，不重打旧标签。

[v0.2.0下载页](https://github.com/KILING-TASI/cn-financial-reconcile/releases/tag/v0.2.0)提供：

- [cn-financial-reconcile-0.2.0-source.zip](https://github.com/KILING-TASI/cn-financial-reconcile/releases/download/v0.2.0/cn-financial-reconcile-0.2.0-source.zip)：完整Skill与源码资源，解压后进入目录即可运行教学示例。
- [cn_financial_reconcile-0.2.0-py3-none-any.whl](https://github.com/KILING-TASI/cn-financial-reconcile/releases/download/v0.2.0/cn_financial_reconcile-0.2.0-py3-none-any.whl)：Python运行包，另提供自己的输入。
- [cn_financial_reconcile-0.2.0.tar.gz](https://github.com/KILING-TASI/cn-financial-reconcile/releases/download/v0.2.0/cn_financial_reconcile-0.2.0.tar.gz)：含教学资源的源码发行包。
- [SHA256SUMS.txt](https://github.com/KILING-TASI/cn-financial-reconcile/releases/download/v0.2.0/SHA256SUMS.txt)：资产校验摘要。

需要Python 3.10+。Windows PowerShell进入已解压的完整源码目录运行：

```powershell
python -m pip install .
python -m cnreconcile examples/demo.json --format html --out local-data/first-report.html
```

打开`local-data/first-report.html`；再次运行请换新文件名。安装可能联网获取普通构建依赖；教学计算离线、只用标准库。

从下载目录安装wheel：

```powershell
python -m pip install .\cn_financial_reconcile-0.2.0-py3-none-any.whl
```

需要读取PDF时，在完整源码目录另运行`python -m pip install ".[pdf]"`；不自动下载原文或安装依赖。可选组件pypdf/pdfplumber保留各自许可。

## 验证和边界

最终包已验证独立安装、教学JSON与HTML、版本、失败不覆盖、Skill与源码资源及许可；完整源码46项回归通过。发布资产摘要以SHA256SUMS.txt为准。标签源码和包内记录保留发布前的候选文案，此页更新为实际发布状态，不覆盖历史产物。

金额一致不等于原文认证；真实材料仅原有选定公司与字段，不是全部财报验收。未验证Skill自然语言发现或浏览器视觉，不提供审计意见、预测或交易指令。原创代码MIT；公告、数据、外部组件权利见THIRD_PARTY_NOTICES.md。不包含第三方PDF、私人材料或作者缓存。旧v0.1.0标签及历史结果保留，用户安装不自动更新。
