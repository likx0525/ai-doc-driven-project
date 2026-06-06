# task-flow

> 文档状态：current

## 需求处理流程

1. 人提出需求。
2. AI 判断是否属于当前版本。
3. AI 判断是否已有相关需求。
4. AI 判断是否涉及业务规则。
5. AI 判断是否涉及数据模型。
6. AI 判断是否需要关键决策。
7. 如需确认，向人提出结构化问题。
8. 已确认需求写入 `requirements.md`。
9. 可执行项写入 `tasks.md`。
10. 更新 `PROJECT_STATE.md`。

## 反馈处理流程

1. 写入 `feedback.md`。
2. 判断反馈类型。
3. 判断是否是 Bug。
4. 判断是否是体验问题。
5. 判断是否是业务规则问题。
6. 判断是否是数据模型问题。
7. 判断是否需要人确认。
8. 如需确认，向人提出结构化问题。
9. 确认后写入 `decisions.md`。
10. 转化为 `tasks.md`。
11. 必要时补充 `test-cases.md`。
12. 再执行开发或修复。

## 完成任务后必须更新

- `tasks.md`
- `PROJECT_STATE.md`
- `TRACEABILITY.md`
- `requirements.md`
- `feedback.md`
- `decisions.md`
- `docs/test/`
- `docs/artifacts/`
- `DOCS_INDEX.md`
- `LESSONS_LEARNED.md`，如产生长期经验
- `RULE_CHANGE_REQUESTS.md`，如发现规则体系缺失或不合理
- `docs/ai-dev/concurrency/`，如存在多会话、锁、changeset 或冲突
- `docs/ai-dev/changesets/`，如本次通过 changeset 提交或合并
- `DOC_UPDATE_TRIGGERS.md` 触发的相关文档。
