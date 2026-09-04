# Unit economics and KPIs

Estate2Code does not invent savings. A customer assessment should measure its existing discovery, documentation, conversion, review and remediation effort.

## Value model

```text
labor capacity released = baseline manual hours - measured assisted hours
conversion value = labor capacity released × loaded hourly cost
expected incident value = change-failure reduction × measured incident cost
net value = conversion value + expected incident value - implementation and operating cost
```

Report low, expected and high cases. Do not treat avoided-risk estimates as realized revenue.

## KPIs

| Domain | Measures |
|---|---|
| Discovery | inventory coverage, stale resources, unknown owners |
| Conversion | supported resources, generated resources, manual edits per resource |
| Fidelity | no-change plan rate, property coverage, replacement detection |
| Delivery | time to first managed plan, import throughput, review lead time |
| Reliability | failed imports, rollbacks, post-adoption change failure rate |
| Adoption | active repositories, repeat executions, contributed mappings |
