# MANUAL_GENERATION_RULES.md

## 目标

产品手册、使用说明书、快速开始和 FAQ 必须由项目事实文档驱动生成。

AI Agent 不得凭空编写说明书，不得把未实现、未确认、未测试的内容写成正式可用功能。

---

## 手册内容来源

说明书内容必须来源于以下文档：

- `docs/ai-dev/requirements.md`
- `docs/ai-dev/decisions.md`
- `docs/ai-dev/TRACEABILITY.md`
- `docs/product/PRODUCT_SPEC.md`
- `docs/product/USER_FLOWS.md`
- `docs/product/UI_SPEC.md`
- `docs/product/GLOSSARY.md`
- `docs/business/BUSINESS_RULES.md`
- `docs/business/STATE_FLOWS.md`
- `docs/test/test-cases.md`
- `docs/test/test-runs.md`
- `docs/ai-dev/feedback.md`
- `docs/artifacts/ARTIFACTS.md`
- `docs/deploy/CHANGELOG.md`

---

## 手册状态

手册条目状态包括：

- draft：草稿，来自已确认需求或设计，但尚未验证；
- verified：已验证，功能已实现并通过测试或人工验收；
- published：已发布，进入正式用户说明；
- deprecated：已废弃，功能已移除或说明已过期；
- pending-confirmation：待确认，内容需要用户确认。

---

## 什么时候必须更新手册

以下情况必须检查并更新手册：

1. 新功能完成；
2. 用户流程变化；
3. UI 页面、按钮、字段、文案变化；
4. 业务规则变化；
5. 状态流变化；
6. 错误提示变化；
7. 新增测试用例；
8. 测试执行通过；
9. 新增截图；
10. 用户反馈暴露常见问题；
11. 发布新版本；
12. 功能废弃或移除。

---

## 不允许写入正式手册的内容

以下内容不得写入正式用户手册：

1. 未确认需求；
2. 未实现功能；
3. 未验证功能；
4. AI 推测的操作步骤；
5. 只存在于概念图中的界面；
6. 未经确认的业务规则；
7. 开发内部术语；
8. 敏感信息；
9. 测试账号密码；
10. 未脱敏截图。

如果需要记录，应放入 draft 或 pending-confirmation 状态。

---

## 手册条目生成规则

每个用户手册条目必须包含：

- 编号；
- 标题；
- 状态；
- 适用对象；
- 功能用途；
- 前置条件；
- 操作步骤；
- 操作结果；
- 注意事项；
- 常见问题；
- 关联需求；
- 关联用户流程；
- 关联界面；
- 关联测试；
- 关联截图；
- 最后更新时间。

---

## 用户手册条目模板

### MAN-001：功能或操作标题

#### 状态

draft / verified / published / deprecated / pending-confirmation

#### 适用对象

……

#### 功能用途

……

#### 前置条件

……

#### 操作步骤

1. ……
2. ……
3. ……

#### 操作结果

……

#### 注意事项

- …

#### 常见问题

- …

#### 关联需求

- R-001

#### 关联用户流程

- UF-001

#### 关联界面

- UI-001

#### 关联业务规则

- BR-001

#### 关联测试

- TC-001
- TR-001

#### 关联截图

- ART-001

#### 最后更新时间

YYYY-MM-DD

---

## Quick Start 生成规则

`QUICK_START.md` 只包含用户第一次使用产品所需的最短路径。

Quick Start 内容必须满足：

1. 步骤少；
2. 不解释复杂规则；
3. 不包含未发布功能；
4. 优先引用已验证流程；
5. 面向真实用户，不使用开发术语。

Quick Start 应来源于：

- `PRODUCT_SPEC.md`
- `USER_FLOWS.md`
- `UI_SPEC.md`
- `test-runs.md`
- `USER_MANUAL.md`

---

## FAQ 生成规则

FAQ 应主要来源于：

- 用户反馈 `feedback.md`；
- Bug 报告 `bug-reports.md`；
- 说明书中容易误解的步骤；
- 测试中发现的常见错误；
- 业务规则中的例外情况；
- 部署或环境中的常见问题。

FAQ 条目模板：

### FAQ-001：问题

#### 问题

……

#### 回答

……

#### 适用场景

……

#### 关联功能

- MAN-001

#### 关联反馈

- FB-001

#### 关联规则

- BR-001

#### 状态

draft / published / deprecated

---

## 截图使用规则

用户手册中的截图必须满足：

1. 来源于真实界面截图，或明确标记为 AI 生成概念图；
2. 截图不得包含敏感信息；
3. 截图必须保存到 `docs/artifacts/screenshots/`；
4. 截图必须登记到 `docs/artifacts/ARTIFACTS.md`；
5. 手册中只能引用 `ARTIFACTS.md` 中登记过的截图；
6. 如果 UI 改动导致截图过期，必须标记截图为 deprecated 或更新截图。

---

## 手册与测试的关系

正式说明书中的核心操作步骤必须能对应至少一个测试用例或测试记录。

如果某个手册条目没有测试记录，应标记为：

draft 或 pending-confirmation

不得标记为 verified 或 published。

---

## 手册与 TRACEABILITY.md 的关系

每个正式功能应在 `docs/ai-dev/TRACEABILITY.md` 中建立关系：

需求 → 业务规则 → 用户流程 → 界面 → 任务 → 测试 → 使用说明

如果功能没有对应手册条目，AI Agent 应在任务结果中提示：

“该功能尚未生成用户说明。”

---

## 手册更新后的检查

AI Agent 更新手册后必须检查：

1. 是否引用了已确认需求；
2. 是否引用了已验证流程；
3. 是否引用了已登记截图；
4. 是否没有写入未实现功能；
5. 是否没有暴露敏感信息；
6. 是否更新了 `TRACEABILITY.md`；
7. 是否需要更新 FAQ；
8. 是否需要更新 `QUICK_START.md`；
9. 是否需要用户验收手册内容。
