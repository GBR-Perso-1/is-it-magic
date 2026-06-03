---
paths:
  - "**/*.tf"
  - "**/*.tfvars"
  - "**/terraform*"
---

# Terraform / HCL Language Rules

## Naming
- Resources: snake_case, descriptive (`resource_type.descriptive_name`)
- Variables: snake_case with clear purpose
- Outputs: snake_case matching the resource they expose
