# logs

> 文档状态：current

## 用途

`logs/samples/` 只保存用于问题分析的日志样本。

## 规则

- 不保存大量运行日志。
- 不保存敏感信息。
- 不保存真实密钥。
- 不保存 token。
- 不保存 cookie。
- 日志样本应按日期和问题命名。
- 如果日志包含测试环境敏感信息，必须脱敏后才能进入 `logs/samples/`。

## 命名示例

- `samples/20260516-build-error.log`
- `samples/20260516-runtime-error.log`
