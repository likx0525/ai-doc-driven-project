# ai-doc-driven-project

`ai-doc-driven-project` 是面向 Codex 的 AI 文档治理 skill，用于初始化、审计和升级项目内的文档结构。

它会在目标项目中创建单一根入口 `AGENTS.md`、`docs/` 下的项目事实文档、`.codex/agents` 下的 Codex agent 配置、可选 hooks、线程协调检查、文档影响检查、架构检查、敏感信息安全规则，以及默认关闭的本地自动提交策略。

English README: [README.md](README.md)

## 包结构

- `packages/zh`：中文 skill 包。
- `packages/en`：英文 skill 包。

## 从源码安装 / 使用

```bash
python packages/en/bin/apply_skill.py init --target /path/to/project --dry-run
python packages/en/bin/apply_skill.py init --target /path/to/project --write

python packages/zh/bin/apply_skill.py init --target /path/to/project --dry-run
python packages/zh/bin/apply_skill.py init --target /path/to/project --write
```

## 校验

```bash
python -m pytest
python scripts/clean_runtime_artifacts.py
python packages/zh/bin/validate_skill_package.py --root packages/zh
python packages/en/bin/validate_skill_package.py --root packages/en --english
```

## 许可证

仓库源码使用 MIT License。由模板生成到目标项目中的文件可并入目标项目，并由目标项目的许可证管理；详见 `TEMPLATE_OUTPUT_LICENSE.md`。

## 安全

不要在公开 issue 中粘贴真实凭据、私有日志、个人信息或生产数据。安全问题请按 `SECURITY.md` 处理。
