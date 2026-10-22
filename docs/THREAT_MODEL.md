# Lightweight threat model (STRIDE)
Scope: the simulated portal and its CI/CD. These are design controls, not proof of security; verify with your own scans.
| Threat | Example | Mitigation in this project | Residual risk |
|---|---|---|---|
| Spoofing | Fake admin | Admin page shows synthetic data only; no admin actions | No authentication (future work) |
| Tampering | SQL injection, modified image | Parameterised queries, input validation, tests; image built once and deployed as is | No image signing |
| Repudiation | No audit trail | Jenkins build history, archived reports | App has no audit log |
| Information disclosure | Real data typed into form | Banner warning; server rejects emails and long numbers; no real data by design | Pattern checks are heuristic |
| Denial of service | Request flooding | Request size limit, small footprint | No rate limiting or WAF |
| Elevation of privilege | Container escape, Jenkins takeover | Non-root container, security groups restrict admin ports to your IP, IMDSv2, encrypted disks | Docker socket on Jenkins host; HTTP without TLS |
| Supply chain | Vulnerable dependency | Pinned dependencies, Trivy fs and image scans | New CVEs appear after scans |
