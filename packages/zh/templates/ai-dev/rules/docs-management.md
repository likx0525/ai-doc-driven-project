# docs-management

> 文档状态：current

## 文档放置规则

- `AGENTS.md` 放在根目录，作为 AI 工作入口和任务路由的权威文件。
- 其他管理文档放入 `docs/`。
- 所有核心文档必须登记到 `docs/ai-dev/DOCS_INDEX.md`，供人和 AI 快速理解文档体系。
- 创建、补齐、归档、废弃、重命名任何目录或文档时，必须同步更新 `DOCS_INDEX.md`。
- 每次任务完成前，必须根据 `docs/ai-dev/DOC_UPDATE_TRIGGERS.md` 检查应更新文档。
- 文档必须有状态：current / draft / deprecated / superseded / reference。
- 不得覆盖已有文档。
- 不得删除旧文档。
- 过期文档应标记 deprecated。
- 需要归档时，必须先建议并等待用户确认。
- 归档目录为 `docs/archive/`。
- 文档冲突必须记录，不得自行武断选择。

## 事实来源优先级

1. 用户最新明确确认。
2. `docs/ai-dev/decisions.md`。
3. `docs/ai-dev/PROJECT_STATE.md`。
4. `docs/ai-dev/requirements.md`。
5. `docs/test/` 中已验证结果。
6. 当前代码实际行为。
7. 旧文档 / README / 临时笔记。
8. 聊天上下文。

聊天上下文优先级最低。

## 多会话编辑规则

1. 单会话时，可以直接修改核心文档。
2. 多会话时，优先通过 changeset 提交修改建议。
3. 核心文档同一时间只能被一个会话持有 write 锁。
4. 发现其他会话正在修改核心文档时，不得直接覆盖。
5. 多会话下新增编号必须检查现有文档和 pending changesets。
6. 合并 changeset 前必须检查文件冲突和语义冲突。
7. 不能确定是否冲突时，写入 `docs/ai-dev/concurrency/CONFLICTS.md` 并请求用户确认。

## 核心文档直接编辑限制

以下文档在多会话模式下不建议直接编辑，应优先通过 changeset 合并：

- `AGENTS.md`
- `docs/ai-dev/PROJECT_STATE.md`
- `docs/ai-dev/decisions.md`
- `docs/ai-dev/tasks.md`
- `docs/architecture/DATA_MODEL.md`
- `docs/business/BUSINESS_RULES.md`
- `docs/business/STATE_FLOWS.md`
- `docs/security/SECRETS_POLICY.md`
- `docs/deploy/RELEASE_CHECKLIST.md`
- `docs/deploy/ROLLBACK.md`
