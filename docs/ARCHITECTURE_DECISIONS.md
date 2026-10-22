# Architecture decision records (short)
| # | Decision | Reason | Trade-off / alternative |
|---|---|---|---|
| 1 | Flask + SQLite, no front-end framework | Runs on a student laptop; fewer dependencies means a smaller attack surface | SQLite is single-writer; use PostgreSQL (RDS) for real load |
| 2 | Two EC2 instances (CI and app) | Separation of duties and blast radius | Costs more than one server |
| 3 | Jenkins and SonarQube as containers | Reproducible, versioned in Git, easy to rebuild | Docker socket mount gives Jenkins host-level power |
| 4 | Deploy via `docker save` over SSH | No registry or credentials to manage | Not scalable; production would use ECR + ECS/EC2 pull |
| 5 | Terraform with default VPC | Minimal and cheap | Production would use a dedicated VPC, private subnets, ALB with HTTPS |
| 6 | Pinned versions for dependencies, Trivy, scanner | Reproducible, reduces supply-chain surprises | Needs periodic manual updates |
| 7 | Time-based simulated status | Demonstrates tracking without a workflow engine | Not real workflow logic |
