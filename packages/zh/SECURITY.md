# Security Policy

## Supported versions

Security fixes are prioritized for the latest version. Older versions may
receive fixes when the issue is severe and a backport is practical.

## Reporting a vulnerability

Do not disclose secrets, exploit details, private logs, or reproduction data in a
public issue. Use GitHub private vulnerability reporting when available, or contact
the maintainer through the repository's published security contact.

Please include:

- Affected package or file path.
- Version or commit.
- Impact and expected risk.
- Minimal reproduction steps using fake data only.
- Whether the issue affects generated target-project files, package archives, or the skill source itself.

## Scope

In scope:

- Secret scanning bypasses in the bundled scripts.
- Unsafe default hooks, auto-commit, or generated configuration.
- Template behavior that may cause accidental credential exposure.
- Package archives that accidentally include runtime artifacts or secrets.

Out of scope:

- Business logic written by downstream projects after using the skill.
- Real credentials, private data, or production incidents in downstream projects.
- Requests to recover or disclose credentials.
