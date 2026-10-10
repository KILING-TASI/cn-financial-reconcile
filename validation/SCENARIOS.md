# 限定情景验收 · 2026-10-10

在仓库根目录运行 `python validation/run_scenarios.py --out-dir local-data/scenarios-new`。输出目录必须不存在；仅标准库、离线、不依赖其他仓或作者缓存。入口实际调用两条CLI，不以直接调用算法代替CLI验收。

[本批回执](scenarios-20261010-accepted/receipt.json)保存12个情景的输入摘要、实际方法、退出码及检查结果。每个子目录保存input.json、expected.json和actual.json；成功场景另有实际JSON及HTML。预期依据写在expected.json，是简单金额关系与声明约束，不从工具结果反推。金额方法amount-dimensions-2，分红旧教学输入按缺省实际方法dividend-observation-3输出；历史教学产物保持冻结。

|情景|独立预期与反例|
|---|---|
|amount-demo|复用1亿元=10000万元正例及1亿元与1.2亿元冲突；声明原页未核|
|rounding-boundary / rounding-outside|1000元至元显示精度容差0.5元；1000.5包含边界，1000.5001冲突|
|same-money-different-version|同金额原版/重述版不可比，差额留空，不自动选最新版|
|missing-page|数值匹配和证据缺失同时成立|
|future-disclosure|截止日后披露拒绝，目标结果文件不存在|
|dividend-demo|现金120−40=80万元；80/50=1.6；利润100/50=2；支付30万元归属2024不套2025利润|
|declaration-other-year|2024归属宣告不能套2025利润/现金|
|missing-capex|缺资本开支不计算现金结余/覆盖|
|profit-ownership-mismatch|少数/全部权益一次性项不能减归母利润；独立同归属宣告利润覆盖仍保留|
|recipient-mismatch|受益归属不一致时利润覆盖未知，现金观察仍独立|
|dividend-version-conflict|经营指标版本不同拒绝，目标报告目录不存在|

此前单项覆盖见tests/test_engine.py、test_method_counterexamples.py及test_dividend_observation.py；本批补的是持久输入、独立预期和实际CLI结果。新增test_cli_scenarios在临时目录重跑整批，并验证二次运行拒绝且全部旧文件摘要不变。

试跑说明：scenarios-20261010与scenarios-20261010-complete为本地未完成试跑，不纳入PR产物；未删除。首轮发现Windows分红CLI错误输出默认编码不稳定，已统一UTF-8并提供退出码2的中文失败提示；第二轮错误文本断言过窄，已改为实际版本冲突语义。接受批次已全部复跑。

仅教学情景，没有增加真实公司或PDF认证范围。HTML已生成，未做浏览器视觉验收；original_compat/schema2边界、第三方许可及现有真实选定样本结论不变。未合并、未发布、未修改用户Skill安装。


第二限定批：[三组CN代表场景](CN_SCENARIOS.md)复用本入口并补官方历史制度来源；不重写第一批结果。
