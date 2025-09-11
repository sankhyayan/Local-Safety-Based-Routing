# Security Policy

Thank you for helping keep this project and its users safe.

## Supported versions

We provide security fixes for the following:
- main branch (latest commits)
- Released tags, if any, within the last 6 months

Note: Experimental or feature branches (e.g., `checkpoint-*`, `feat-*`, `experiment-*`) are not guaranteed to receive backports.

## Reporting a vulnerability

Please do NOT open public GitHub issues for security reports.

Preferred:
- Use GitHub’s private "Report a vulnerability" feature (Security tab → Report a vulnerability) to create a Security Advisory with details and steps to reproduce.

Alternative (if private reporting isn’t available):
- Email: security@REPLACE_WITH_YOUR_DOMAIN
  - Include a clear description, impact, steps to reproduce, affected versions/commit, and (if possible) a suggested fix.
  - Optionally include a CVSS v3.1 vector for impact assessment.

We will acknowledge receipt within 2 business days.

## Disclosure and remediation timeline

We aim for the following targets (may vary based on complexity and impact):
- Critical severity: fix or viable mitigation within 7 days
- High severity: fix within 30 days
- Medium/Low severity: fix as part of the next planned release

We’ll provide weekly updates while a report is under review and coordinate a publication date with you once a fix or mitigation is available. Please keep details confidential until we announce a fix.

## Scope and testing guidelines

In scope:
- This repository’s code and default configurations
- Public endpoints explicitly deployed by the project owner (if any)

Out of scope:
- Denial of Service (DoS/DDoS), volumetric attacks, or spam
- Social engineering, physical security, and non-technical attacks
- Third-party services and dependencies outside this repo’s control
- Automated vulnerability scans that degrade service or impact others

Rules of engagement:
- Do not access, modify, or exfiltrate data that isn’t yours
- Use test accounts/data where possible
- Avoid degrading availability or stability
- Follow applicable laws and terms of service

## Safe harbor

We will not pursue legal action for good-faith, compliant research that adheres to this policy. If you have concerns about testing scope, contact us before proceeding.

## Credit and recognition

With your consent, we can acknowledge your contribution (name/handle) in release notes or a SECURITY acknowledgments section after a fix is released. If you prefer to remain anonymous, let us know.

## No bug bounty (at this time)

We do not currently offer monetary rewards. High-quality reports are appreciated and help protect users.

---

Maintainers: update `security@REPLACE_WITH_YOUR_DOMAIN` with a monitored inbox, and consider enabling GitHub’s private vulnerability reporting and Dependabot alerts in the repository settings.
