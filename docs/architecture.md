# Architecture and decision boundaries

## Pipeline

1. Normalize Azure Resource Graph, ARM template or canonical JSON.
2. Reject duplicate identifiers and dependency cycles.
3. Compare resource IDs with optional Terraform state.
4. Order unmanaged resources after their declared dependencies.
5. Generate constrained Terraform/OpenTofu and Bicep scaffolds.
6. Report preserved fields, unsupported resources and manual-review requirements.
7. Emit a content digest over the normalized adoption decision.

## Trust boundaries

- Inventory is untrusted input and may be incomplete.
- Terraform state is sensitive and should remain local.
- Generated code is output for review, never an instruction to deploy.
- Provider defaults and computed properties can produce post-import differences.
- Importing state does not change infrastructure, but subsequent plans can.
- Destructive plans should be evaluated with ImpactGraph and accountable human review.

## Live discovery design

A production collector should use GitHub or Azure DevOps workload identity federation and Azure Resource Graph Reader access. Discovery identity must not be able to deploy. Resource responses should be encrypted, scoped and retained only as long as necessary.
