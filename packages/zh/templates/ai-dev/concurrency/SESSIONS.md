# SESSIONS.md

> 文档状态：stub

## 目标

记录当前或近期 AI / Codex 会话，避免多个会话同时修改同一任务或同一核心文档，并追踪上下文压缩次数。

## 会话状态

- `active`：进行中
- `handoff-ready`：已整理交接，等待接管
- `completed`：已完成
- `stale`：疑似过期
- `cancelled`：已取消

## compact_count 规则

- `0`：正常。
- `1`：允许继续，但必须更新关键项目文档。
- `2`：迁移阈值，除小范围收尾外必须 handoff 并新开会话或 fork。
- `3+`：不得继续承担新开发任务，只能整理 handoff 和切换会话。

## 会话模板

### S-YYYYMMDD-001

#### 启动时间
YYYY-MM-DD HH:mm

#### 会话目标
……

#### 线程角色
coordinator / worker / reviewer / explorer / subagent / automation

#### compact_count
0

#### 负责范围
- T-001

#### 计划读取文档
- …

#### 计划修改文档
- …

#### 计划修改代码
- …

#### 当前状态
active / handoff-ready / completed / stale / cancelled

#### 关联 changeset
- CS-YYYYMMDD-001

#### Handoff
- HO-YYYYMMDD-001

---

## 当前会话表

| Session | Thread ID | Role | Goal | compact_count | Status | Locks | Changeset | Handoff | Notes |
|---|---|---|---|---:|---|---|---|---|---|
