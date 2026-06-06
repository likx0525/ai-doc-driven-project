# TEST_SECRETS_FORMAT

> 文档状态：current

本文件只说明本地测试凭据文件格式，**不得在本文件填写真实值**。

真实测试环境或本地开发环境凭据只能写入：

```text
.ai-secrets/test-secrets.local.md
```

该文件必须被 `.gitignore` 排除，不得提交。生产环境凭据不得保存给 AI 使用。

## 推荐格式

```md
# test-secrets.local.md

## 数据库连接

### TEST_DATABASE_URL
用途：
值：<redacted>

### TEST_DATABASE_USER
用途：
值：<redacted>

### TEST_DATABASE_PASSWORD
用途：
值：<redacted>

## API 测试凭据

### TEST_API_BASE_URL
用途：
值：<redacted>

### TEST_API_KEY
用途：
值：<redacted>

### TEST_API_TOKEN
用途：
值：<redacted>

## 测试账号

### TEST_ACCOUNT_USERNAME
用途：
值：<redacted>

### TEST_ACCOUNT_PASSWORD
用途：
值：<redacted>
```

## 安全要求

- 只保存测试环境或本地开发环境凭据。
- 不保存生产环境凭据。
- 不保存真实用户隐私数据。
- 不提交到版本库。
- 测试报告、日志样本、截图和最终回答中必须脱敏。
- 如果 `.ai-secrets/` 已被 git 跟踪，仅修改 `.gitignore` 不会自动取消跟踪，必须先人工处理索引状态。
