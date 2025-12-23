# Security Policy

## Reporting a Vulnerability

**Please do not open public GitHub issues for security vulnerabilities.**

Instead, please report security issues by emailing: **security@vunvulear.dev**

Include the following information:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Affected versions
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt of your report within 48 hours and provide a more detailed response within 5 business days.

## Security Response Process

1. We will confirm the vulnerability and determine its scope
2. We will audit code to find any similar problems
3. We will prepare fixes for all supported versions
4. We will release fixed versions and coordinate public disclosure

## Supported Versions

| Version | Status | Security Support Until |
|---------|--------|----------------------|
| 1.x     | Current | 2025-12-31 |
| 0.x     | Deprecated | 2024-12-31 |

## Security Best Practices

When using Smart Cloud Aggregator:

1. **File Permissions**
   - Ensure IaC files are only readable by authorized users
   - Protect generated reports (they contain sensitive configuration details)

2. **Secrets Management**
   - Do not commit secrets or credentials in IaC files
   - Use secret management solutions (Azure Key Vault, AWS Secrets Manager)

3. **Access Control**
   - Limit who can run the analyzer
   - Protect output reports from unauthorized access

4. **Data Privacy**
   - Be aware that reports contain infrastructure details
   - Do not share reports publicly without review

## Dependencies

Smart Cloud Aggregator has **zero runtime dependencies** and uses only Python standard library. This minimizes potential supply chain vulnerabilities.

## Known Issues

(None currently reported)

For the latest security information, check the [Security Advisories](https://github.com/vunvulear/Cloud.ServiceAggregator/security/advisories) page.
