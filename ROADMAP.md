# 原表定位与更正版本路线

更新日期：2026-10-09。开发版0.2.0.dev1，尚未发布。

已有：金额单位/精度、主体/期间/合并范围/币种/累计单季核对；可选本地PDF引句存在检查。新增：少量金额字段的明确原表行列提取与文档版本关系；不承诺任意PDF自动解析。

## 首版契约
在现有pairs不变的前提下，为提取事实附tableEvidence：physicalPage、tableIndex、rowIndex、columnIndex、headerRowIndex、rowLabel、columnLabel、rawCell、rawRow、rawHeader、bbox、sourceSha256；索引明确从1起，PDF坐标单位点、左上原点。表格存在、引句存在、字段对应与金额勾稽分列，不能互相替代。

现有documents校验id、entity、publishedAt、version、sha256；title与source可保留，但尚未强制校验。后续需将关系依据绑定对应文档摘要，不能把当前引句检查称为完整版本认证。；relations以from/to/type与公告原页依据声明correction/restatement。更正并非全部科目重述，按fields列影响范围；没有更正依据不按晚日期覆盖旧值。重述比较列保留原披露期与本次来源期，防止旧列误标成当期。

首批提取：已声明主体、期间、合并范围、单位和表格位置的营收、归母净利润、经营现金流金额，保留全部比较列。每股收益、比例、OCR、自动选财务口径暂不做。

## 验收
真实公司PDF少量字段：指定表/行/列与原页渲染对应；重述影响字段有公告依据，未影响字段不重写。错行、错列、错主体、累计/单季混合、母公司/合并混合及多比较列歧义不通过。

研究工作台转换：将渠道事实填reported，定位提取事实填extracted，version关系另存；调用reconcile前确认basis/scope/period。独立工具不依赖主Skill，源PDF仅本地核对，不随代码发布。

后续：二家公司/版式适配及更正前后差异视图。真实样本与坐标误差未验收前不称自动抽取全部三表或审计完成。


首批本地验收记录见[限定真实样本](validation/limited-real-samples.json)，数值与版式验证不等于来源实时认证或全部原页完成。

## 开发接口示例

安装可选组件 `python -m pip install .[pdf]`。`cnreconcile.table_extract.extract_amount(spec)`输入本地pdfPath、asOf、完整context和selector，selector包含physicalPage/tableIndex/rowIndex/columnIndex/headerRowIndex/rowLabel/columnLabel。首版金额单位须在行标签明示。返回fact与tableEvidence；将fact接入现有pairs.extracted，渠道值仍需独立填reported。

`validate_versions(documents, relations, as_of)`只登记有页码引句依据的correction/restatement及影响fields，拒绝错主体、错误时间顺序和循环；不自动替换事实。版本关系本轮仅教学输入验证，尚无真实重述样本，不标原文闭环。

本次开发结果分别记录toolVersion、inputSchema和rulesVersion。未发布开发接口不与既有v0.1.0发布包混称；主工作台转换需明确适配版本。

## 更正资料新增（2026-10-09）

[有限更正资料](validation/correction-context.json)已在选定官方原页核对单位与比例更正，但尚未取得原/修订两版对应表。比例不属于本金额核对器输入；单位变化不自动触发旧金额除以一万。此次仅新增证据资料，不能标为validate_versions真实版本链闭环。财务审计与内控审计、审计师变更分别判断。截图因浏览器file协议策略拒绝仍未取得。
