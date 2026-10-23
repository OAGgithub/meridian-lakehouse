---
paths:
  - "src/**/generate*.py"
  - "src/**/transactions*.py"
  - "src/**/bronze/**"
  - "src/**/silver/**"
  - "conf/**"
---

# The transaction schema is fraud-ready — do not trim it

Every transaction record carries all of these, at every layer:

| field | why it exists |
| --- | --- |
| `txn_id` | natural key, idempotent upsert |
| `account_id` | links to account master |
| `counterparty_id` | the other side — required for pass-through detection |
| `counterparty_name` | sanctions/OFAC name screening |
| `amount` | structuring detection (clusters just under reporting limits) |
| `currency` | cross-border risk |
| `timestamp` | tz-aware UTC; velocity rules need ordering |
| `channel` | wire / ach / card / atm / branch — risk differs per channel |
| `direction` | debit / credit — pass-through is in-then-out |
| `merchant_category` | MCC-style risk scoring |
| `country` | geography risk, cross-border |
| `branch_id` | internal fraud, branch-level anomalies |
| `device_id` | account takeover |
| `ip_address` | account takeover, impossible-travel |

These exist so fraud and AML detection can be added as a gold layer later
without regenerating or re-ingesting anything. **Never drop one to
simplify.** If a field seems unused, it is unused *yet*.

If you think a field is genuinely wrong, say so and propose the change in
DECISIONS.md — do not quietly leave it out.
