# knowledge-capture.md

## 目标

AI Agent 在开发、分析问题、测试、调试、部署、使用工具过程中，必须主动识别可复用、可追踪、可验证的信息，并写入项目文档。

聊天上下文不得作为长期记忆。

---

## 什么时候必须回写文档

出现以下情况时，必须回写到对应文档：

1. 发现新的业务规则；
2. 发现新的状态流或状态约束；
3. 发现新的数据模型约束；
4. 发现新的用户操作流程；
5. 发现新的 UI 状态、交互规则或文案规则；
6. 发现新的测试用例或边界场景；
7. 发现 bug 根因；
8. 发现环境配置步骤；
9. 发现依赖安装、构建、运行、部署注意事项；
10. 发现工具使用的更优方式；
11. 发现敏感信息处理要求；
12. 发现性能、兼容性、可访问性问题；
13. 发现外部服务、API、Webhook 调用规则；
14. 发现日志、监控、故障处理经验；
15. 发现当前规则体系缺失或不合理；
16. 发现重复出现的问题、误区或易错点；
17. 发现多会话冲突、编号冲突、锁状态变化或 changeset 合并经验。

---

## 什么信息不需要回写

以下信息一般不需要沉淀，避免文档噪音：

1. 一次性临时操作；
2. 无长期价值的中间推理；
3. 已经在文档中存在的重复内容；
4. 未验证的猜测；
5. 过于细碎的普通代码修改；
6. 和项目无关的工具过程；
7. 无法确认的个人偏好；
8. 没有后续指导意义的失败尝试。

不确定是否值得记录时，优先记录到 `LESSONS_LEARNED.md` 的“待确认经验”区域，而不是写入正式规则。

---

## 文档回写位置

AI Agent 必须根据内容类型写入对应文档：

### 需求相关

写入：

- `docs/ai-dev/requirements.md`
- `docs/ai-dev/tasks.md`
- `docs/ai-dev/TRACEABILITY.md`

### 关键决策

写入：

- `docs/ai-dev/decisions.md`

### 使用反馈和问题

写入：

- `docs/ai-dev/feedback.md`
- `docs/test/bug-reports.md`

### 经验和教训

写入：

- `docs/ai-dev/LESSONS_LEARNED.md`

### 规则改进建议

写入：

- `docs/ai-dev/RULE_CHANGE_REQUESTS.md`

### 架构经验

写入：

- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/MODULES.md`
- `docs/architecture/DATA_MODEL.md`
- `docs/architecture/ARCHITECTURE_CHECKLIST.md`

### 产品和用户流程

写入：

- `docs/product/PRODUCT_SPEC.md`
- `docs/product/USER_FLOWS.md`
- `docs/product/UI_SPEC.md`
- `docs/product/GLOSSARY.md`

### 产品手册、使用说明和 FAQ

写入：

- `docs/manual/MANUAL_GENERATION_RULES.md`
- `docs/manual/MANUAL_INDEX.md`
- `docs/manual/USER_MANUAL.md`
- `docs/manual/QUICK_START.md`
- `docs/manual/FAQ.md`

### 业务逻辑

写入：

- `docs/business/BUSINESS_RULES.md`
- `docs/business/STATE_FLOWS.md`

### 开发流程和接口

写入：

- `docs/development/DEVELOPMENT_GUIDE.md`
- `docs/development/API_CONTRACTS.md`
- `docs/development/CODE_CONVENTIONS.md`

### 数据和迁移

写入：

- `docs/data/DATA_LIFECYCLE.md`
- `docs/data/MIGRATIONS.md`
- `docs/data/BACKUP_RESTORE.md`

### 测试

写入：

- `docs/test/test-cases.md`
- `docs/test/test-runs.md`
- `docs/test/bug-reports.md`

### 环境和运行

写入：

- `docs/env/environment.md`
- `docs/env/runbook.md`
- `docs/env/dependencies.md`
- `docs/env/credentials-note.md`

### 部署和发布

写入：

- `docs/deploy/DEPLOYMENT.md`
- `docs/deploy/RELEASE_CHECKLIST.md`
- `docs/deploy/ROLLBACK.md`
- `docs/deploy/OPERATIONS.md`
- `docs/deploy/CHANGELOG.md`

### 工具使用

写入：

- `docs/codex/CODEX_WORK_MODE_SELECTION.md`
- `docs/codex/CODEX_APP_USAGE.md`
- `docs/codex/CODEX_USAGE_LOG.md`

### 多会话协作与冲突

写入：

- `docs/ai-dev/concurrency/SESSIONS.md`
- `docs/ai-dev/concurrency/LOCKS.md`
- `docs/ai-dev/concurrency/MERGE_QUEUE.md`
- `docs/ai-dev/concurrency/CONFLICTS.md`
- `docs/ai-dev/changesets/pending/`
- `docs/ai-dev/LESSONS_LEARNED.md`
- `docs/ai-dev/RULE_CHANGE_REQUESTS.md`

### 产物

写入：

- `docs/artifacts/ARTIFACTS.md`

### 日志、监控、事故

写入：

- `docs/observability/LOGGING.md`
- `docs/observability/MONITORING.md`
- `docs/observability/INCIDENTS.md`

### 安全、隐私、权限、敏感信息

写入：

- `docs/security/SECURITY.md`
- `docs/security/PRIVACY.md`
- `docs/security/PERMISSIONS.md`
- `docs/security/SECRETS_POLICY.md`

---

## 回写原则

AI Agent 回写文档时必须遵守：

1. 只记录有长期价值的信息；
2. 不把猜测写成事实；
3. 不把临时结论写成正式规则；
4. 不重复写入已有内容；
5. 不覆盖已有决策；
6. 不把测试环境敏感信息写入 docs/；
7. 不把未确认的业务规则写成已确认；
8. 不把代码中存在的行为直接视为正确需求；
9. 需要用户确认的内容应写为“待确认”；
10. 规则变化必须有来源，例如任务、反馈、测试、决策或审查结果。

---

## 每次任务结束前必须执行的检查

AI Agent 每次任务完成前，必须检查：

1. 是否产生新的需求？
2. 是否产生新的业务规则？
3. 是否产生新的数据模型约束？
4. 是否产生新的用户流程？
5. 是否产生新的测试用例？
6. 是否发现新的 bug 根因？
7. 是否发现新的环境配置步骤？
8. 是否发现新的部署或回滚注意事项？
9. 是否发现新的工具使用经验？
10. 是否有规则需要改进？
11. 是否需要更新 `TRACEABILITY.md`？
12. 是否需要更新 `DOCS_INDEX.md`？
13. 是否需要根据 `DOC_UPDATE_TRIGGERS.md` 更新其他文档？
14. 是否需要更新 `ARTIFACTS.md`？
15. 是否有内容应写入 `LESSONS_LEARNED.md`？
16. 是否有内容应写入 `RULE_CHANGE_REQUESTS.md`？
17. 是否发现并发会话、锁、changeset 或冲突需要记录？

如果有，必须更新对应文档。

如果没有，应在任务结果中写明：

“本次未产生需要沉淀的新规则或经验。”
