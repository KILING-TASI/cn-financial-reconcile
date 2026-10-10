# 输入预检与差异排查

```powershell
python -m cnreconcile.preflight --contract
python -m cnreconcile examples/demo.json --validate-only
```

契约为cnreconcile-pairs-v1，截止日asOf与pairs必填。每对reported/extracted须声明entity、metric、period、scope、currency、basis、source、publishedAt、unit、value。金额单位仅元/千元/万元/亿元；statementVersion为可选非空版本说明，未声明不等于同版。契约索引不是JSON Schema。

--dry-run是--validate-only的别名；仅本地字段检查，输出JSON到stdout，不联网、不读取PDF、不创建报告，不接受--out或其他format。返回declared-fields-valid不表示数值吻合、原页核验或声明口径真实。错误列出fieldPath，退出码2；可能同时保留多条缺字段错误。文件大小限制16MB，最多10000项配对是程序限制，不是性能认证。

正式核对出现数值差异或口径不可比时，JSON/Markdown/HTML提供reviewHints排查提示：字段名、单位/精度、主体/期间、合并/母公司、累计/单季、币种和修订版本；涉及含税/不含税时另查定义与注释。输入明确不同时列为declared-conflict，其余是review-only。提示不是已确认原因，不能根据差额反推营业总收入/营业收入，也不调大容差或改原值。数值吻合仍不等于原页核验。

教学路径可继续用examples/demo.json；故意删除其中事实的source或unit即可查看预检路径错误，无须试跑计算或准备PDF。
