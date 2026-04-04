# Sub-processor and Vendor Register

**ConsolidaSuite** -- Financial Consolidation Platform

**Last Updated:** 2026-04-03

---

## Overview

This register documents all third-party vendors and sub-processors engaged in connection with the ConsolidaSuite platform. It is maintained pursuant to Art. 28 GDPR and updated whenever a sub-processor is added, changed, or removed.

---

## Active Vendors

| Vendor | Service | Data Processed | DPA Status | Location | Notes |
|--------|---------|---------------|------------|----------|-------|
| Hetzner Online GmbH | Cloud hosting infrastructure (compute, storage, networking) | All application data including user accounts, financial data, HR/payroll data, audit logs | DPA in place (Hetzner standard DPA per Art. 28 GDPR) | EU (Germany -- Falkenstein/Nuremberg data centers) | Primary infrastructure provider; all data remains within EU |
| Let's Encrypt (Internet Security Research Group) | Automated SSL/TLS certificate issuance | Domain names only | No DPA required | US (certificate authority operations) | No personal data is processed; only domain name validation for certificate issuance; exempt from DPA requirement |

---

## Vendor Assessment Notes

### Hetzner Online GmbH

- **Website:** https://www.hetzner.com
- **Service type:** Infrastructure as a Service (IaaS)
- **Data center locations:** Germany (EU)
- **Certifications:** ISO 27001
- **DPA:** Available at https://www.hetzner.com/legal/privacy-policy -- standard DPA compliant with Art. 28 GDPR
- **Data processing:** All ConsolidaSuite application data is hosted on Hetzner infrastructure. This includes databases, application servers, and backup storage.
- **Review date:** [LAST REVIEW DATE]
- **Next review due:** [NEXT REVIEW DATE]

### Let's Encrypt (ISRG)

- **Website:** https://letsencrypt.org
- **Service type:** Certificate Authority
- **Data processed:** Domain names submitted for certificate issuance (no personal data)
- **DPA:** Not required -- no personal data is transmitted or processed
- **Review date:** [LAST REVIEW DATE]
- **Next review due:** [NEXT REVIEW DATE]

---

## Vendors NOT Used

The following categories of third-party services are explicitly **not** used by ConsolidaSuite:

| Category | Status | Notes |
|----------|--------|-------|
| Analytics services (e.g., Google Analytics, Mixpanel) | Not used | No third-party analytics are deployed |
| Advertising / tracking networks | Not used | No advertising or tracking of any kind |
| Third-party AI services in production | Not used | No customer data is sent to external AI providers at runtime |
| CDN providers | Not used | Content served directly from Hetzner infrastructure |
| Email marketing platforms | Not used | No marketing emails are sent via third-party services |
| Customer support / ticketing platforms | Not used | [TO BE EVALUATED IF NEEDED] |
| Payment processors | Not used | [TO BE EVALUATED WHEN BILLING IS IMPLEMENTED] |

---

## Change Log

| Date | Change | Approved By |
|------|--------|-------------|
| 2026-04-03 | Initial register created | [APPROVER NAME] |

---

## Review Schedule

This vendor register is reviewed:

- At least **annually** as part of the regular compliance review.
- **Before** engaging any new sub-processor.
- **After** any significant change to an existing sub-processor relationship.

The Data Protection Officer ([DPO EMAIL ADDRESS]) is responsible for maintaining this register.

---

*Maintained by [DPO NAME], Data Protection Officer.*
