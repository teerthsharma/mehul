# Hygiene Checks

| Check | Severity | Meaning |
|---|---|---|
| utm_persistence | high | Registration page not persisting UTM to person profile — all downstream attribution broken |
| test_accounts | medium | Test accounts inflate funnels and corrupt conversion rates |
| host_scoping | medium | Demo traffic contaminating production metrics |
| utm_stitching | low | UTM landing pages not converting — landing page experience problem |
| chapter_number_gap | medium | chapter_number not reliably set on all events |

## Escalation
If utm_persistence fail rate >10% of registrations: block immediately and alert
