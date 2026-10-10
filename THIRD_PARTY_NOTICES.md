# 许可范围与第三方说明

核对日期：2026-10-09。根LICENSE既有版权署名research-workbench contributors保持不变。本项目有权授权的原创代码/原创说明采用MIT；不能据此替第三方或来源不明内容授权。

## 本批代码来源

本批`table_extract.py`是项目新增的显式表格定位与版本关系实现；调用外部pdfplumber/pypdf读取组件，不打包其库源码或二进制。未发现本批代码引入其他项目代码，不将这项检查扩展为整个代码历史的原创证明。

## 依赖、示例与未确认范围

Python标准库随使用者Python发行版；可选[pdfplumber](https://github.com/jsvine/pdfplumber/blob/stable/LICENSE.txt)采用MIT，读取链的传递依赖须按实际安装版本保留许可。可选[pypdf](https://github.com/py-pdf/pypdf/blob/main/LICENSE)采用BSD-3-Clause。这些库未捆绑；本清单不是完整递归软件物料清单，不自动认证未来版本。

examples/demo.json是虚构教学输入；readme-preview.html由其实际计算生成，不是真实基金或公司数据，只追加教学/日期标识，未取得截图或浏览器视觉验收。页面未捆绑字体，只使用系统后备字体。validation仅保留有限事实、来源URL和摘要，不附公告全文、PDF、机构图表、行情缓存或账户输入。

原文的访问或公开披露不等于已获再分发权；管理人、巨潮等原件和数据的商业再分发授权未确认，用户须按实际用途核对。MIT仅覆盖有权授权的项目内容，不授予外部行情、研报、公告、品牌或运行依赖的权利。


## 同作者旧接口迁入

cnreconcile/original_compat.py 的schema-1字段核验及日期/URL辅助从research-workbench提交1594937的scripts/verify_original.py、collection_validation.py、research_library.py迁入，保留MIT及原版权；本次只剥离schema-2分支（留主包暂未迁移），并拒绝未知显式schema。不是重新认证原文/完整三表。源码与许可证：[原始提交](https://github.com/KILING-TASI/research-workbench/tree/1594937)。主包不再维护这一份schema-1核验核心，旧名称仅转发；独立工具不需要安装工作台。
