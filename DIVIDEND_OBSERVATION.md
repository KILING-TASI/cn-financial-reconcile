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


## 语义返修：方法 dividend-observation-2

新版入口使用 examples/dividend-teaching-v2.json；旧输入与旧结果冻结保留，不代表新版已核验利润归属。每个事实的 metric 必须与外层六字段严格相同，营收不能冒充经营现金流。未知显式 inputSchema / methodVersion（包括 null）拒绝；未声明版本的旧输入按本轮明确方法输出并记实际版本，不重写历史。

输入schema为 cnreconcile-dividend-v1，方法为 dividend-observation-2。利润及一次性项须明确 profitAttribution=parent-owners 或 all-owners，taxBasis=after-tax；宣告分红利润覆盖还须 recipientAttribution 匹配。缺口或不一致时相关利润数留空，现金观察与利润观察分开。before-tax不能与税后利润直接相减。合并范围相同不能证明归属相同。

statementVersion仅为选定版本声明，相同文字不证明原文同版；versionSelectionStatus始终为声明未核验。不自动选更正优先级。更正前后真实原文配对仍未完成。历史结果不可作为本轮新版方法验收。

新版教学产物见 [v2结果](examples/dividend-observation-v2-result.json) 与 [v2报告](examples/dividend-observation-v2-report.html)。旧样本没有归属与税后声明，在新版方法中利润调整/覆盖未知。


## 官方原文限定样本（方法 dividend-observation-3）

新增 public-document-sample，仅接受HTTPS来源、原文SHA、物理页、短引句、sourceValue/明确转换及unitQuote。提供本地原文时核主体/年度、文件SHA、金额token和单位引句；无本地PDF时仅声明未核页，不升级证据。教学方法2仍可显式调用，方法1/未知版本拒绝；缺省方法输出实际版本3。金额绑定不等于全量报表或会计分类认证。

[美的2025年限定样本](examples/midea-dividend-report.html)：深交所官方276页年报，选取物理页11/79/135/137/223的六项。经营现金流533.46亿元，购建项111.42亿元，结余代理422.04亿元，年度预案323.61亿元，观察覆盖1.30倍。归母税后利润和非经常性损益扣税/少数权益后归属声明一致，调整利润412.67亿元。实际支付304.77亿元含跨年度分红，不把利息或回购凑进股息。所有六项在本地绑定页找到短引句/单位/金额；公开输入无私人路径，重新跑公开输入仍为声明未核页。

仅选定这份原文，不认证最新更正版本、母公司可分配现金或未来派息。合并现金结余不等于母公司现金，购建项不含收购。真实更正前后配对仍按取得情况单独列状态，不能用一份更正公告当两版报表。
