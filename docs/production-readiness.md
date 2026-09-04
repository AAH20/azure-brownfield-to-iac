# Production acceptance requirements

The current release proves the compiler pipeline against a synthetic estate. Production adoption additionally requires:

- Azure Resource Graph pagination and throttling tests.
- Resource-type fixtures captured from authorized subscriptions.
- Terraform provider-schema validation for every generated argument.
- Known, unknown, sensitive and computed-value handling.
- Subresources, extension resources and cross-scope dependencies.
- Current API-version discovery rather than static versions.
- Azure Verified Module compatibility mapping.
- Secret redaction before reports or logs are persisted.
- `terraform plan` or OpenTofu plan after import.
- ARM What-If comparison for Bicep.
- Explicit approval for every replacement or deletion.
- State locking, backup, encryption and recovery procedures.
- False-positive and manual-correction measurements.

Compilation alone is not evidence of semantic equivalence.
