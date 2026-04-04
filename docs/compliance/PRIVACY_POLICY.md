# Privacy Policy

**ConsolidaSuite** -- Financial Consolidation Platform

**Last Updated:** 2026-04-03

---

## 1. Data Controller

| Field | Details |
|-------|---------|
| Company | [COMPANY NAME] |
| Address | [COMPANY ADDRESS] |
| Data Protection Officer | [DPO NAME] |
| DPO Email | [DPO EMAIL ADDRESS] |
| Registration Number | [COMPANY REGISTRATION NUMBER] |

For any privacy-related inquiries, please contact the Data Protection Officer at [DPO EMAIL ADDRESS].

---

## 2. Personal Data We Collect

### 2.1 User Account Data

| Data Element | Description |
|-------------|-------------|
| Email address | Used for authentication and communication |
| Full name | Used for identification within the platform |
| Role / permissions | Used for role-based access control (RBAC) |
| Password (hashed) | Stored as a bcrypt hash; plaintext is never retained |

### 2.2 Employee Records (HR/Payroll Module)

| Data Element | Description |
|-------------|-------------|
| Employee name | Identification of employees within client organizations |
| Employee email | Communication and record linkage |
| Position / title | Organizational context |
| Salary data | Gross pay, net pay, tax withholdings, benefits |

### 2.3 Audit Logs

| Data Element | Description |
|-------------|-------------|
| IP address | Source of the request |
| User-agent string | Browser/client identification |
| Timestamp | When the action occurred |
| User ID | Who performed the action |
| Action performed | What was done |
| Resource affected | Which record or entity was changed |

---

## 3. Purpose of Processing

| Data Category | Purpose |
|--------------|---------|
| User account data | Providing and managing access to ConsolidaSuite, authenticating users, enforcing role-based permissions |
| Employee records | Processing HR and payroll consolidation on behalf of the data controller (client organization) |
| Financial data | Financial statement consolidation, intercompany transaction management, tax compliance, fixed asset tracking, treasury management |
| Audit logs | Ensuring platform security, detecting unauthorized access, maintaining accountability, and meeting regulatory audit requirements |

---

## 4. Legal Basis for Processing (Art. 6 GDPR)

| Data Category | Legal Basis | GDPR Article |
|--------------|-------------|--------------|
| User account data | Performance of a contract -- necessary to provide the service the user has registered for | Art. 6(1)(b) |
| Employee records (HR/payroll) | Performance of a contract -- processing on behalf of client organizations under a Data Processing Agreement | Art. 6(1)(b) |
| Financial records | Legal obligation -- statutory requirements for financial record retention (e.g., tax law, accounting regulations) | Art. 6(1)(c) |
| Audit logs | Legitimate interest -- maintaining the security and integrity of the platform, detecting and preventing unauthorized access | Art. 6(1)(f) |

For processing based on legitimate interest (audit logs), we have conducted a balancing test and concluded that the security interest outweighs the minimal impact on data subjects, given that only technical metadata is collected and access to logs is restricted.

---

## 5. Data Retention Periods

| Data Category | Retention Period | Rationale |
|--------------|-----------------|-----------|
| User accounts | Duration of active account + 30 days after account deletion | Allows for account recovery and ensures clean deletion |
| Financial data | 7 years from the end of the relevant fiscal year | Statutory retention requirements for financial records |
| Audit logs | 3 years from creation | Sufficient for security investigations and regulatory audits |
| Backups | 30 days (rolling) | Disaster recovery; automatically overwritten |
| Session tokens | Duration of session (access token: 15 minutes, refresh token: 7 days) | Minimum necessary for authentication |

After the applicable retention period, data is permanently deleted or irreversibly anonymized.

---

## 6. Third-Party Processors

We use the following third-party service providers to process personal data on our behalf:

| Processor | Service | Data Processed | Location | DPA Status |
|-----------|---------|---------------|----------|------------|
| Hetzner Online GmbH | Cloud hosting infrastructure | All application data | EU (Germany) | DPA in place |
| Let's Encrypt (ISRG) | SSL/TLS certificates | Domain names only (no personal data) | N/A | No DPA required |

We do not use any third-party analytics services, advertising networks, or tracking tools.

---

## 7. International Data Transfers

ConsolidaSuite processes all personal data exclusively within the European Union / European Economic Area (EU/EEA). No personal data is transferred to countries outside the EU/EEA.

Our hosting infrastructure is located in Hetzner data centers in Germany. No sub-processors are located outside the EU/EEA that would receive personal data.

---

## 8. Your Rights as a Data Subject

Under the GDPR, you have the following rights regarding your personal data:

### 8.1 Right of Access (Art. 15)

You have the right to obtain confirmation as to whether personal data concerning you is being processed, and to receive a copy of that data.

### 8.2 Right to Rectification (Art. 16)

You have the right to have inaccurate personal data corrected without undue delay.

### 8.3 Right to Erasure (Art. 17)

You have the right to request deletion of your personal data where it is no longer necessary for the purpose for which it was collected, subject to legal retention obligations.

### 8.4 Right to Data Portability (Art. 20)

You have the right to receive your personal data in a structured, commonly used, and machine-readable format, and to transmit that data to another controller.

### 8.5 Right to Restriction of Processing (Art. 18)

You have the right to request restriction of processing in certain circumstances, such as when you contest the accuracy of the data.

### 8.6 Right to Object (Art. 21)

You have the right to object to processing based on legitimate interest. We will cease processing unless we demonstrate compelling legitimate grounds.

### 8.7 How to Exercise Your Rights

To exercise any of these rights, contact our Data Protection Officer:

- **Email:** [DPO EMAIL ADDRESS]
- **Post:** [COMPANY NAME], Attn: Data Protection Officer, [COMPANY ADDRESS]

We will respond to your request within 30 days. If we require an extension, we will inform you within the initial 30-day period, providing our reasons. There is no fee for exercising your rights unless requests are manifestly unfounded or excessive.

### 8.8 Right to Lodge a Complaint

You have the right to lodge a complaint with a supervisory authority in the EU Member State of your habitual residence, place of work, or place of the alleged infringement. Our lead supervisory authority is [SUPERVISORY AUTHORITY NAME AND CONTACT].

---

## 9. Cookie Policy

### 9.1 Cookies We Use

ConsolidaSuite uses only strictly necessary functional cookies for authentication:

| Cookie Name | Purpose | Type | Duration |
|------------|---------|------|----------|
| `access_token` | JWT authentication token | HTTP-only, Secure, SameSite=Strict | 15 minutes |
| `refresh_token` | Token renewal | HTTP-only, Secure, SameSite=Strict | 7 days |

### 9.2 No Analytics or Tracking Cookies

We do not use any analytics cookies, tracking cookies, advertising cookies, or third-party cookies of any kind.

### 9.3 Consent

These cookies are strictly necessary for the functioning of the service and are exempt from the consent requirement under Article 5(3) of the ePrivacy Directive (2002/58/EC). No cookie consent banner is required or displayed.

### 9.4 Disabling Cookies

You may disable cookies in your browser settings. However, doing so will prevent you from logging into ConsolidaSuite, as the authentication cookies are required for the service to function.

---

## 10. Data Security Measures

We implement appropriate technical and organizational measures to protect personal data:

| Measure | Description |
|---------|-------------|
| Encryption in transit | All data transmitted over TLS 1.2 or higher |
| Password hashing | User passwords hashed with bcrypt (cost factor 12+) |
| Role-based access control (RBAC) | Users can only access data permitted by their assigned role |
| Audit logging | All significant actions are logged with timestamp, user, IP, and action |
| Rate limiting | API endpoints are rate-limited to prevent brute-force attacks |
| Input validation | All user input is validated and sanitized |
| Secure session management | HTTP-only, Secure, SameSite=Strict cookies |
| Infrastructure security | Hosted on Hetzner Cloud with firewall rules and regular security updates |

---

## 11. Changes to This Policy

We may update this Privacy Policy from time to time to reflect changes in our practices or legal requirements. When we make material changes:

- We will update the "Last Updated" date at the top of this policy.
- For significant changes, we will notify registered users via email.
- Continued use of the service after changes constitutes acceptance of the updated policy.

We encourage you to review this policy periodically.

---

## 12. Contact Information

For questions, concerns, or requests related to this Privacy Policy or our data processing practices:

| Channel | Details |
|---------|---------|
| Data Protection Officer | [DPO EMAIL ADDRESS] |
| General inquiries | [GENERAL CONTACT EMAIL] |
| Postal address | [COMPANY NAME], [COMPANY ADDRESS] |
| Website | [COMPANY WEBSITE URL] |

---

*This Privacy Policy is effective as of 2026-04-03.*
