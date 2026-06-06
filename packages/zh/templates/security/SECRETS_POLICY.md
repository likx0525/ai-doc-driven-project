# SECRETS_POLICY

> 文档状态：current

## 原则

- 测试环境敏感信息允许保存。
- 保存位置只能是 `.ai-secrets/`。
- `.ai-secrets/` 必须加入 `.gitignore`。
- `docs/` 中不得保存真实敏感值。
- 测试报告、日志、截图必须脱敏。
- 生产环境凭据默认禁止保存。
- 如用户明确授权保存生产类凭据，必须单独标记高风险，并不得提交版本库。

## 允许保存的范围

- 测试环境数据库连接串。
- 测试环境数据库用户名和密码。
- 测试环境 API key。
- 测试环境 token。
- 测试环境账号密码。
- 测试环境服务地址。
- 本地开发环境密钥。
- 专门为 AI 测试创建的临时凭据。

## 禁止保存的范围

除非用户明确书面确认，不保存生产环境密码、生产环境数据库连接信息、生产环境 token、真实用户账号密码、真实用户隐私数据、私钥、长期有效的高权限凭据、可访问生产数据的凭据。

## 保存位置

真实值只能保存到：

- `.ai-secrets/test-secrets.local.md`
- `.ai-secrets/*.local.md`

禁止保存到：

- `docs/`
- `logs/`
- `docs/artifacts/`
- `docs/test/`
- `docs/env/credentials-note.md`
- `docs/env/environment.md`
- `docs/env/runbook.md`
- `README.md`
- `AGENTS.md`
- 任何会提交到版本库的文档

## AI 使用规则

- AI 可以读取 `.ai-secrets/test-secrets.local.md` 执行测试环境连接测试。
- 不在最终回答、测试报告、日志样本、截图、代码、commit message 中输出真实密钥。
- 测试记录只能写已使用测试环境凭据、凭据来源、测试结果和脱敏后的连接目标。

## 脱敏示例

`postgres://test_user:****@test-db.local:5432/test_db`

## 凭据泄露处理流程

1. 停止继续扩散。
2. 标记为敏感信息泄露风险。
3. 建议用户轮换该凭据。
4. 将相关文件列入待清理任务。
5. 清理或脱敏前不得继续引用该敏感信息。
6. 如涉及生产环境，必须请求用户确认后再处理。
