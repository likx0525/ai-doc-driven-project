# WORKTREES

> 文档状态：stub

## 目标

记录 Codex-managed worktree 或长期并行 worktree 的创建、范围、状态、合并和回退方式。

## 使用规则

1. 大型重构、跨模块改动、替代方案探索优先使用 worktree 隔离。
2. worktree 输出不是项目事实，必须通过主线程 merge policy。
3. worktree 必须有 owner、scope、base revision、目标文件、测试计划和回退方式。
4. 合并前必须运行文档影响检查、架构检查和线程协调检查。

## 记录表

| Worktree ID | Date | Branch/path | Base | Scope | Owner | Status | Handoff | Merge decision | Rollback |
|---|---|---|---|---|---|---|---|---|---|
