# AUTO_COMMIT_POLICY

> 文档状态：current

## 目标

定义项目级可选自动提交策略。这里的“自动提交”只指 **本地 git commit**；默认不自动 stage、不自动 commit，且永远不自动 push。

该策略用于降低长任务、文档结构升级、批量治理修复后的收尾成本，但不能替代用户确认、测试、敏感信息检查或主线程合并决策。

## 默认策略

| 等级 | 含义 | 默认状态 |
|---|---|---|
| `disabled` | 不允许自动 stage 或自动 commit | 默认 |
| `manual_suggest` | 只输出提交计划和建议命令 | 推荐默认 |
| `stage_only` | 允许脚本 stage 明确列出的路径，不 commit | 可选 |
| `local_commit` | 允许脚本在检查通过后创建本地 commit | 需要显式启用 |
| `push` | 自动 push 到远端 | 禁止 |

## 硬性约束

- 自动提交默认关闭。
- 只有 `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json` 和命令行同时显式允许时，才能执行本地 commit。
- 不允许自动 push。远端 push、PR、merge 必须由用户或外部 CI 流程显式处理。
- 不允许提交 `.ai-secrets/`、`.env`、私钥、证书、kubeconfig、真实 token、真实密码或真实用户隐私数据。
- 不允许在 active write / merge 锁冲突、merge queue blocked/conflict、compact_count 达到迁移阈值且未 handoff 时自动提交。
- 不允许用自动提交绕过 `ai_doc_impact_check.py`、`thread_coordination_check.py`、`architecture_check.py`。
- 不允许把未确认业务规则、数据模型、权限规则、状态流或历史数据解释写入 commit message 作为已确认事实。
- 自动提交不得把 subagent / fork / worktree 的候选结论直接变成项目事实；仍必须由主线程采纳。

## 启用步骤

1. 阅读本文件和 `AGENTS.md` 的自动提交规则。
2. 编辑 `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`，将 `enabled` 和需要的能力改为 `true`。
3. 优先创建工作分支，避免在 `main`、`master`、`production`、`prod`、`release` 等保护分支上自动提交。
4. 先运行：

```bash
python scripts/project_auto_commit.py --plan
```

5. 只在确认变更范围、检查项和提交信息后，才运行本地提交：

```bash
python scripts/project_auto_commit.py --commit -m "docs: update AI governance strategy"
```

如需让脚本 stage 路径，必须明确列出路径：

```bash
python scripts/project_auto_commit.py --auto-stage --paths AGENTS.md docs/ai-dev/git/AUTO_COMMIT_POLICY.md --commit -m "docs: add auto-commit policy"
```

## 推荐提交粒度

- 一次 commit 只做一个语义主题。
- 文档治理升级、业务功能、重构、测试修复、安全修复应分开提交。
- 大量文件变化应优先使用 worktree、changeset 或人工 commit review。
- 自动提交适合文档结构升级、检查脚本同步、轻量规则修正；不适合高风险生产改动。

## 提交信息格式

推荐：

```text
<type>: <summary>

- Why: <reason>
- Scope: <key files or modules>
- Checks: <commands run>
- Docs: <docs updated>
```

提交信息不得包含真实密钥、真实 token、真实密码、真实用户隐私数据、未确认业务承诺或未经确认的生产状态。

## 完成后输出

使用自动提交策略后，任务结果必须说明：

```text
自动提交策略：disabled/manual_suggest/stage_only/local_commit
是否执行本地 commit：是/否
commit hash：<hash>/无
是否执行 push：否
提交前检查：已执行/未执行；结果
未提交内容：有/无；说明
```
