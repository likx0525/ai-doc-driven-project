# CODEX_SUBAGENTS

> 文档状态：current

## 目标

定义 Codex subagents 和项目 `.codex/agents/*.toml` 的使用规则。

## 项目 agents

- `main-session-coordinator`：主线程协调、最终合并和事实归档。
- `thread-manager`：线程、锁、compact_count、handoff、merge queue 维护。
- `merge-coordinator`：合并前审查。
- `architecture-reviewer`：架构边界审查。
- `code-explorer`：只读代码探索。
- `docs-reviewer`：文档一致性审查。
- `security-reviewer`：敏感信息、隐私、权限风险审查。
- `test-reviewer`：测试证据和验证声明审查。

## 使用规则

1. 只有用户或主线程明确要求时才使用 subagents。
2. 使用前必须明确工作包、范围、允许/禁止修改路径和预期输出。
3. subagent 输出默认不是项目事实。
4. subagent 结果必须通过 `THREAD_HANDOFFS.md` 和 `MERGE_POLICY.md` 进入主线程评审。
5. 涉及敏感信息时，优先使用主线程 + `security-reviewer`，不得扩散未脱敏信息。

## 合并前检查

```bash
python scripts/thread_coordination_check.py --strict --record
python scripts/ai_doc_impact_check.py --task-type subagent --record
```

## 记录表

| Date | Agent | Role | Scope | Files changed | Handoff | Main decision | Notes |
|---|---|---|---|---|---|---|---|
