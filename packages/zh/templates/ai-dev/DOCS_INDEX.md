# DOCS_INDEX.md

> 文档状态：current

## 用途

登记项目内 AI 文档驱动开发所需文档的用途、状态、可信度和事实来源属性。新增、废弃、替代、归档或重命名文档时必须更新本文件。

## 状态枚举

- `stub`：模板占位，尚未填充，不可作为事实源。
- `draft`：草案，可参考但需要确认或补充。
- `current`：当前有效事实源或规则源。
- `verified`：经过测试、运行结果或用户确认的事实源。
- `deprecated/reference`：旧版或参考材料，不作为当前入口或当前事实源。
- `superseded`：已被其他文档替代。

## 可信度规则

- 空模板、占位内容、示例内容默认可信度低。
- `current` 不等于“事实已完整”；只表示该文档是当前应该维护的位置。
- 业务规则、数据模型、状态流、权限、隐私、历史数据解释必须经过用户确认或可验证证据支持，才可标为高可信事实。

## 文档索引

| 文档路径 | 用途 | 初始状态 | 可信度 | 是否事实来源 | 备注 |
|---|---|---|---|---|---|
| `AGENTS.md` | Codex 根入口；入口索引、任务路由、硬性门禁 | current | 高 | 是，规则源 | 入口规则源 |
| `docs/ai-dev/DOCS_INDEX.md` | 文档索引、状态和可信度登记 | current | 高 | 是，规则源 | 文档新增/归档/废弃/状态变化时更新 |
| `docs/ai-dev/DOC_UPDATE_TRIGGERS.yml` | 机器可读文档更新触发规则 | current | 高 | 是，规则源 | `ai_doc_impact_check.py` 优先读取 |
| `docs/ai-dev/DOC_UPDATE_TRIGGERS.md` | 文档更新触发规则的人读说明 | current | 高 | 是，规则源 | 必须与 YAML 同步 |
| `docs/ai-dev/PROJECT_STATE.md` | 当前项目状态、阶段、风险、待确认事项 | stub | 低 | 否，填充后才可作为事实源 | 初始化后必须尽快补全 |
| `docs/ai-dev/PROJECT_AUDIT.md` | 接管审查结果 | draft | 中 | 部分 | audit 模式重点维护 |
| `docs/ai-dev/requirements.md` | 需求记录 | stub | 低 | 否，确认后才是事实源 | 需求确认后更新状态/可信度 |
| `docs/ai-dev/feedback.md` | 用户反馈、审查发现 | stub | 低 | 部分 | 反馈需转化为任务/需求/缺陷 |
| `docs/ai-dev/decisions.md` | 用户确认或项目采纳的关键决策 | stub | 低 | 否，记录确认后才是事实源 | 不记录未经确认推断 |
| `docs/ai-dev/tasks.md` | 任务清单、状态、后续工作 | stub | 低 | 部分 | 任务完成前更新 |
| `docs/ai-dev/TRACEABILITY.md` | 需求、决策、任务、测试、手册追踪 | stub | 低 | 部分 | 功能完成、手册更新时维护 |
| `docs/ai-dev/LESSONS_LEARNED.md` | 经验、教训、避免重复错误 | stub | 低 | 部分 | 任务结束前评估是否沉淀 |
| `docs/ai-dev/RULE_CHANGE_REQUESTS.md` | 规则改进建议 | stub | 低 | 部分 | 不直接修改规则时先记录建议 |
| `docs/ai-dev/rules/` | 任务流、文档管理、安全、知识沉淀等规则 | current | 中/高 | 是，规则源 | 项目实际规则变更需记录 |
| `docs/ai-dev/orchestration/` | 工作模式、线程、worktree、subagents、handoff、merge policy | current | 中/高 | 是，规则源 | 多线程输出默认不是事实 |
| `docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md` | 主线程、thread-manager、merge-coordinator、reviewer、explorer、subagent 的角色权限规则 | current | 高 | 是，规则源 | 非主线程输出默认不是事实 |
| `docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md` | Codex `/compact`、自动 compact、compact_count 阈值和新会话 handoff 规则 | current | 高 | 是，规则源 | compact_count >= 2 时必须迁移或收尾 |
| `docs/ai-dev/orchestration/THREAD_COORDINATION.md` | 主线程协调多会话、锁、合并队列和压缩迁移的检查清单 | current | 高 | 是，规则源 | 与 thread_coordination_check.py 配套 |
| `docs/ai-dev/concurrency/` | 多会话、锁、合并队列、冲突记录 | stub | 低 | 部分 | 有并发协作时维护 |
| `docs/ai-dev/changesets/` | pending/merged/rejected 文档变更集 | stub | 低 | 部分 | 多会话或高风险文档改动时使用 |
| `docs/ai-dev/doc-update-runs/` | 文档影响检查运行记录 | stub | 低 | 部分 | `ai_doc_impact_check.py --record` 生成 |
| `docs/ai-dev/thread-check-runs/` | 线程协调、agent 角色、compact_count、锁和合并队列检查记录 | stub | 低 | 部分 | `thread_coordination_check.py --record` 生成 |
| `docs/architecture/ARCHITECTURE.md` | 整体架构说明 | stub | 低 | 否，填充后才可作为事实源 | 重大架构变更需 ADR |
| `docs/architecture/MODULES.md` | 模块说明 | stub | 低 | 否，填充后才可作为事实源 | 与 MODULE_BOUNDARIES.yml 同步 |
| `docs/architecture/MODULE_BOUNDARIES.yml` | 机器可读模块边界和依赖约束 | stub | 低 | 否，填充并检查后才可作为事实源 | `architecture_check.py` 优先读取 |
| `docs/architecture/DATA_MODEL.md` | 数据模型 | stub | 低 | 否，确认后才可作为事实源 | 涉及历史数据必须确认 |
| `docs/architecture/ARCHITECTURE_CHECKLIST.md` | 修改前架构检查清单 | current | 中 | 是，规则源 | 架构敏感修改前读取 |
| `docs/architecture/ARCHITECTURE_DEBT.md` | 架构债务 | stub | 低 | 部分 | 重构建议不得冒充事实 |
| `docs/architecture/ADR/` | 架构决策记录 | stub | 低 | 部分 | 重大决策时创建 ADR |
| `docs/codex/` | Codex App 能力选择、使用规则和记录 | current | 中/高 | 是，规则源 | 使用能力后必要时记录 |
| `docs/product/` | 产品规格、用户流程、UI、术语 | stub | 低 | 否，填充确认后才可作为事实源 | 手册生成必须追溯到这里 |
| `docs/business/` | 业务规则和状态流 | stub | 低 | 否，用户确认后才可作为事实源 | 不把代码行为直接当业务事实 |
| `docs/development/` | 开发指南、接口契约、代码约定、依赖策略 | stub | 低 | 部分 | 以项目实际技术栈补全 |
| `docs/data/` | 数据生命周期、迁移、备份恢复 | stub | 低 | 否，确认后才可作为事实源 | 数据变更必须维护 |
| `docs/quality/` | 非功能、性能、兼容性、可访问性 | stub | 低 | 部分 | 需测试或约束来源支持 |
| `docs/security/` | 安全、隐私、权限、密钥策略 | draft | 中 | 部分 | 不保存真实敏感信息 |
| `docs/integrations/` | 外部集成、外部 API、Webhook | stub | 低 | 部分 | 凭据只写说明，不写真实值 |
| `docs/observability/` | 日志、监控、事故 | stub | 低 | 部分 | 日志样本必须脱敏 |
| `docs/env/` | 环境、运行手册、依赖、凭据格式说明 | draft | 中 | 部分 | `TEST_SECRETS_FORMAT.md` 不填写真实值 |
| `docs/test/` | 测试计划、用例、运行记录、缺陷报告 | stub | 低 | 部分 | 未执行测试不得声称通过 |
| `docs/manual/` | 用户手册、快速开始、FAQ | stub | 低 | 否，生成后需追溯事实源 | 不能脱离产品/测试事实编写 |
| `docs/deploy/` | 部署、发布、回滚、运维、版本 | stub | 低 | 部分 | 未部署不得声称成功 |
| `docs/artifacts/` | AI 产物说明和索引 | current | 中 | 是，规则源 | 截图、报告、临时产物不得散放根目录 |
| `logs/README.md` | 日志样本管理说明 | current | 中 | 是，规则源 | 真实日志必须脱敏 |
| `scripts/ai_doc_impact_check.py` | 文档影响检查脚本 | current | 高 | 否 | 完成前优先运行 |
| `scripts/architecture_check.py` | 架构边界检查脚本 | current | 高 | 否 | 架构敏感修改前/后运行 |
| `scripts/thread_coordination_check.py` | 线程协调、agent 角色、compact_count、锁和合并队列强制检查脚本 | current | 高 | 否 | 并发/compact/subagent/合并前运行 |
| `docs/ai-dev/git/AUTO_COMMIT_POLICY.md` | 项目自动提交可选策略；只允许显式启用的本地 commit | current | 高 | 是，规则源 | 默认关闭，永不自动 push |
| `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json` | 自动提交能力开关和保护路径配置 | current | 中 | 是，规则源 | 项目可修改；默认禁用 |
| `scripts/project_auto_commit.py` | 自动提交计划和显式本地 commit 辅助脚本 | current | 高 | 否 | 只在配置和 CLI 双重启用时 commit |
| `.codex/agents/` | Codex agents 配置 | current | 中 | 否 | 必须包含 developer_instructions；不是根入口 |
| `.codex/hooks.json` | Codex lifecycle hooks 示例配置 | draft | 中 | 否 | 需要在 Codex 中审查并信任后生效 |
| `.ai-secrets/` | 本地测试敏感信息目录 | current | 高 | 否 | 必须从版本库排除 |

## 维护规则

- `AGENTS.md` 是 Codex 根入口。
- 旧文档不得直接删除；过期时标记为 `deprecated/reference` 或 `superseded`。
- 文档冲突必须记录到 `docs/ai-dev/concurrency/CONFLICTS.md` 或 `docs/ai-dev/PROJECT_AUDIT.md`。
- 聊天上下文不是长期事实来源，关键结论必须落到项目文档。
