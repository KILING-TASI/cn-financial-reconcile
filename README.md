# 中国财报金额核对

把渠道数据和原文提取的金额放在一起，先核对报表口径，再看数字是否一致，并列出尚未核实的原页证据。

[![原创代码 MIT](https://img.shields.io/badge/原创代码-MIT-blue)](LICENSE)

## 安装和首次试用

本轮对应[发布页](https://github.com/KILING-TASI/cn-financial-reconcile/releases/tag/v0.2.4)；下载时以实际上传的完整源码、wheel、sdist 与校验清单为准。源码按下面步骤安装；下载 wheel 后，将安装命令末尾的 `.` 换成该 wheel 文件路径。pip 安装不会自动注册 AI 工具中的 Skill。

本轮源码版本为 `0.2.4`。统一安装入口需要 Python 3.10 或以上。在完整源码目录新建自己的 Python 环境，下面的 Windows 命令不需要激活脚本：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\cn-financial-reconcile.exe --help
.\.venv\Scripts\cn-financial-reconcile.exe demo --out-dir reports/demo --auto-name
```

工具名与仓库名相同；在已激活的环境中可以直接输入工具名。Linux/macOS 使用 `.venv/bin/python` 和 `.venv/bin/cn-financial-reconcile`。教学结果写入当前工作目录；`--auto-name` 自动另选新名字，旧结果保留。不加该参数时，教学入口拒绝已有目录。`cn-financial-reconcile run --help` 查看原生参数，原来的命令继续兼容。pip 安装提供 CLI；作为 Skill 使用仍须保留完整源码及许可资源，不能只复制 SKILL.md。安装可能需要联网获取普通构建依赖；教学离线。下面保留原生入口及此前发行记录，本轮安装和版本以本节为准。

导入自己的资料前，可先运行 `python -m cnreconcile input.json --validate-only`；[输入契约索引](examples/INPUT_CONTRACTS.md)列出字段、入口与预检限制。

## 最短试用

需要Python 3.10+。下载[完整源码ZIP](https://github.com/KILING-TASI/cn-financial-reconcile/releases/download/v0.2.0/cn-financial-reconcile-0.2.0-source.zip)，解压后进入目录；也可使用本仓`main`源码。获取源码需要联网，下面的教学示例只用标准库，不联网，也不需要安装PDF组件。

在Windows PowerShell中运行：

```powershell
python -m cnreconcile examples/demo.json --format html --out local-data/first-report.html
```

打开`local-data/first-report.html`查看核对结果。输出文件必须是新文件；再次运行时换一个名字，例如`second-report.html`，旧报告不会被覆盖。

需要机器读取的结果时，运行`python -m cnreconcile examples/demo.json`，标准输出为JSON。输入格式参照[教学输入](examples/demo.json)，金额支持人民币元、千元、万元、亿元；舍入精度须按原文显示方式明确声明。

## 实际结果示例

[已生成的教学HTML（下载后打开）](examples/filter-sort-preview.html) · [教学输入](examples/demo.json) · [原教学预览及生成记录](examples/readme-preview-manifest.json)

|教学配对|核对结果|
|---|---|
|1亿元与10000万元|金额一致；原页引句仅有声明，本次未核原页|
|1亿元与1.2亿元|相差2000万元，需要回查渠道值和提取过程|

这些金额来自人为教学样本，不是真实公司披露。HTML已经生成，尚未完成浏览器视觉验收；数值一致不等于来源或会计分类已认证。

## 能做什么，暂不支持什么

- 核对已整理的金额，区分数值一致、舍入范围内一致、数值冲突和口径不可比。合并与母公司、累计与单季、不同币种或声明版本不能直接混比。
- 对指定位置的少量原表字段、物理页引句及选定更正前后字段作检查；保留来源和证据状态，不自动替换旧事实。
- 观察已整理的经营现金流、资本开支、利润与分红金额，区分分红所属年度和实际支付年度。

不自动采集全部财报，不解析任意PDF或提供OCR；不自动选最新版、判断非经常损益分类、认证分红批准阶段，也不把含利息的混合现金支出整项当股息。每股收益、比率、汇率换算和预测不在基础金额核对范围内。结果供研究复查，不是审计意见。

保存报告成功后会在stderr提示结果位置和打开文件；默认JSON的stdout保持可解析。已有输出请换新名字，缺PDF组件按可选依赖安装，非法输入核对字段、单位、日期和版本；不提供覆盖旧结果的选项。

金额方法与反例见[方法说明](METHODS.md)，原表定位及输入契约见[接口说明](ROADMAP.md)，分红的条件、选定样本与缺口见[分红观察说明](DIVIDEND_OBSERVATION.md)。

## 独立使用与项目关系

本仓既提供[Skill调用说明](SKILL.md)，也提供可单独运行的Python引擎：Skill的`name`和发行包名都是`cn-financial-reconcile`，命令行模块名为`cnreconcile`。使用Skill需保留本仓代码、示例及说明资源，不能只复制SKILL.md；Skill安装和自然语言发现不在本轮验证范围内。

[研究工作台](https://github.com/KILING-TASI/research-workbench)可以按约定调用本工具，但本工具不依赖工作台、其他自家仓库或作者缓存。公司研究的判断仍由研究工作台组织，金额核对不自动给出投资结论。

需要安装到选定的Python环境时，在本仓源码根目录运行：

```powershell
python -m pip install .
```

安装通常需要联网获取普通构建组件`setuptools>=68`，也可使用已准备好的本地依赖源。只有需要读取本地PDF时才安装可选组件：

```powershell
python -m pip install ".[pdf]"
```

该extra使用`pypdf>=4,<7`和`pdfplumber>=0.11,<0.12`。缺组件、无法提取文字或引句未找到，都不能算原页通过。PDF只在本地读取，不上传；工具不自动安装组件或下载原文。

完整源码ZIP和sdist包含Skill说明、教学示例与验证资源；wheel包含运行代码，不包含源码仓的`examples/`和`validation/`。只安装wheel时，请自行提供符合契约的输入，不要假定当前目录已有教学文件。

## 源码与下载版本

当前`main`已包含金额核对、选定原文与版本对照、分红观察及情景测试，此前v0.2.0发行记录保留如下，当前版本以上方安装节为准；[v0.2.0已于2026-10-10发布](https://github.com/KILING-TASI/cn-financial-reconcile/releases/tag/v0.2.0)。下载[完整源码ZIP](https://github.com/KILING-TASI/cn-financial-reconcile/releases/download/v0.2.0/cn-financial-reconcile-0.2.0-source.zip)、[wheel](https://github.com/KILING-TASI/cn-financial-reconcile/releases/download/v0.2.0/cn_financial_reconcile-0.2.0-py3-none-any.whl)或[sdist](https://github.com/KILING-TASI/cn-financial-reconcile/releases/download/v0.2.0/cn_financial_reconcile-0.2.0.tar.gz)，并用[SHA256SUMS.txt](https://github.com/KILING-TASI/cn-financial-reconcile/releases/download/v0.2.0/SHA256SUMS.txt)核对摘要。安装步骤见[发布说明](RELEASE_NOTES.md)。

[旧版Release v0.1.0](https://github.com/KILING-TASI/cn-financial-reconcile/releases/tag/v0.1.0)是此前的研究预览版，不包含本次新增接口；本轮没有重新验证旧包，也不会自动更新用户安装。

## 验证、许可与来源

[持续检查](https://github.com/KILING-TASI/cn-financial-reconcile/actions/workflows/tests.yml)覆盖Windows/Linux、Python 3.10/3.12，以及单仓导出后的安装与教学运行。测试通过不代表所有财报版式、真实取数或投资判断通过。

[教学CLI情景](validation/SCENARIOS.md)保存输入、独立预期、实际结果及方法版本；[中国上市公司代表情景](validation/CN_SCENARIOS.md)补充官方规则来源与支持条件；[单仓隔离安装检查](.github/scripts/validate_isolated_install.py)验证不依赖其他仓库。真实原文仅限说明中选定的公司、字段与出现位置，不扩展为完整财报认证。

原创代码和有权授权的说明采用[MIT](LICENSE)；外部组件、公告、数据和品牌保留各自权利，见[第三方与数据范围](THIRD_PARTY_NOTICES.md)。不打包第三方PDF、私人账户或作者缓存。更多使用边界见[免责声明](DISCLAIMER.md)。

## 导入前先预检

`python -m cnreconcile input.json --validate-only`（或`--dry-run`）只检查本地声明字段，不联网、不读PDF、不写报告，也不执行专业计算。问题按fieldPath列出；通过不证明来源或完整性。`python -m cnreconcile.preflight --contract`查看契约索引。完整入口与边界见[输入契约说明](examples/INPUT_CONTRACTS.md)。

## 一个真实原文问题的完整案例

[美的2025年报现金覆盖案例](examples/midea-cash-coverage-20261010/README.md)保存问题、官方来源、六项原页核对、结果与复现办法。仅回答选定年度现金覆盖问题，不冒充完整公司估值或未来支付承诺。原PDF只本地留存，不再分发。

本轮基金/财报新报告采用结论、关键缺口、完整证据三层阅读；保存页面已做[桌面与窄屏浏览器验收](validation/browser-20261010/README.md)。旧快照按原记录保留，不因此自动标为已验。

0.2.4修正安装后的案例工具方法路径定位；原计算与0.2.3公开案例快照保留。工作台beta.10兼容矩阵记录的是固定0.2.3接口组合；本补丁不改变schema1接口，但不把新版本自动标成原组合已验。
