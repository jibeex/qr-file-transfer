# Security Policy

**Owner**: Security Lead  
**Review trigger**: On each release, or when a vulnerability is reported

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.x (pre-release) | ✅ Active development |

---

## Reporting a Vulnerability

**Do not file a public GitHub issue for security vulnerabilities.**

Report privately via email to: `security@[project-email]` (replace with actual address)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

Expected response: acknowledgement within 48 hours, fix timeline within 14 days for critical issues.

---

## Threat Model

This tool is designed for **air-gapped environments**. The threat model is documented in `docs/DESIGN.md §7`.

### What the system protects against

- Data corruption (SHA-256 file integrity + CRC32 per-chunk verification)
- Injection attacks (input path sanitization, parameter validation)
- Accidental data leakage to external services (zero network access, verifiable)

### What the system does NOT protect against

- **Confidentiality**: Data is visible on screen during transfer — no encryption in v1.0
- **Authentication**: No digital signatures; cannot verify who encoded the file
- **Physical access**: Unauthorized recording of the screen by a bystander
- **Insider threats**: A malicious user can use the tool to exfiltrate data (see UC-005 in REQUIREMENTS.md)

### Planned security enhancements (v2.0+)

- Optional AES-256-GCM encryption before encoding
- Ed25519 digital signatures for sender authenticity
- HMAC-SHA256 to replace CRC32 for per-chunk integrity
- Metadata anonymization (strip filename from QR video)

---

## Security Design Principles

1. **Zero network access** — the tool makes no outbound connections, ever
2. **Local processing only** — all data stays on the local filesystem
3. **Fail-safe defaults** — integrity check failures abort and do not write output
4. **No telemetry** — no analytics, crash reporting, or data collection
5. **Input validation first** — all user inputs sanitized before use (path traversal, type checks)

---

## Known Limitations

| Limitation | Severity | Mitigation |
|---|---|---|
| No encryption | High (for sensitive data) | Use in physically secure environments; v2.0 will add optional encryption |
| CRC32 not cryptographically secure | Medium | SHA-256 at file level is cryptographic; CRC32 is for error detection only |
| Video file contains raw file data | Medium | Secure-delete video files after transfer |
| SSD secure delete limitations | Low | Documented in `docs/DESIGN.md §7.6` |
