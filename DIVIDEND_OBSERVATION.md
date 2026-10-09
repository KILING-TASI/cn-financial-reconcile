# 分红可持续性观察（开发中，教学验收）

用于回答：宣告分红有多少利润和现金支撑？实际支付发生在哪年？先限定非金融公司、明确年度金额；本批为教学输入，未完成公开公司原文样本验收。

从仓库根目录运行：
```sh
python -m cnreconcile.dividend_observation examples/dividend-teaching.json --out-dir local-data/dividend
```
输出 input.json、result.json、报告.md、报告.html，拒绝覆盖已有目录。

每条事实沿用金额核对的 entity、metric、period、publishedAt、scope、currency、basis、source、unit、value，并声明 statementVersion。年度口径 basis=annual。金额可混用元/千元/万元/亿元但先统一单位；主体、范围、币种必须一致。经营现金流、资本开支、利润、一次性收益期间和已选更正版本必须相同。这里验证声明一致，不认证原文，也不自动选择更正版本。

宣告分红按 attributablePeriod 关联所属年度；实际支付按 period 关联现金发生年度，另保留 attributablePeriod。宣告和支付不是同一件事，不把二者合计。资本开支须为非负现金支出，来源应说明定义；一次性收益金额由输入明确分类，不自动认定非经常性损益。

现金结余代理=经营现金流−资本开支；现金覆盖=结余/同口径分红。利润覆盖只对同年度宣告分红观察，利润减所列一次性收益单列，不等同可分配利润或严格FCFF。缺项、不同年度、非正现金结余或零分红不强算安全倍数。财务观察不预测未来分红，不统一打分，不代替会计判断。

教学样本：经营现金流120万元、资本开支40万元、利润100万元、一次性收益20万元；宣告50万元，现金覆盖1.6倍，利润覆盖2倍。2025年实际支付30万元属于2024年度，单列支付观察，不混入2025年度宣告评价。全部教学值，未核原文。

验证包含期间/范围/更正版本冲突、缺资本开支、负或零现金结余、零分红、分红所属其他年度。未完成自动更正版本选择、原文样本核验、金融公司适配与浏览器视觉验收。


[本批教学报告](examples/dividend-observation-report.html)（下载后查看，未完成浏览器视觉验收）；[计算结果](examples/dividend-observation-result.json)。
