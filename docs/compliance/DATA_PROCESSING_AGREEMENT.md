# Data Processing Agreement

**ConsolidaSuite** -- Financial Consolidation Platform

**Last Updated:** 2026-04-03

---

This Data Processing Agreement ("DPA") forms part of the agreement between the Client ("Controller") and [COMPANY NAME] ("Processor") for the provision of ConsolidaSuite services ("the Service").

---

## 1. Definitions

| Term | Definition |
|------|-----------|
| **Controller** | The Client organization that determines the purposes and means of processing personal data through the Service. |
| **Processor** | [COMPANY NAME], which processes personal data on behalf of the Controller in the course of providing the Service. |
| **Sub-processor** | A third party engaged by the Processor to carry out specific processing activities on behalf of the Controller. |
| **Personal Data** | Any information relating to an identified or identifiable natural person, as defined in Art. 4(1) GDPR. |
| **Processing** | Any operation performed on personal data, as defined in Art. 4(2) GDPR. |
| **Data Subject** | An identified or identifiable natural person whose personal data is processed. |
| **Supervisory Authority** | An independent public authority established by an EU Member State pursuant to Art. 51 GDPR. |
| **Data Breach** | A breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to, personal data. |

---

## 2. Subject Matter and Duration

### 2.1 Subject Matter

This DPA governs the processing of personal data by the Processor on behalf of the Controller in connection with the provision of ConsolidaSuite, a multi-entity financial consolidation platform.

### 2.2 Duration

This DPA shall remain in effect for the duration of the service agreement between the Controller and the Processor. Upon termination of the service agreement, the provisions of this DPA relating to data deletion or return (Section 11) shall apply.

---

## 3. Nature and Purpose of Processing

The Processor processes personal data for the following purposes:

1. **Providing the Service** -- Hosting and operating the ConsolidaSuite platform, including user authentication, role-based access control, and data storage.
2. **Financial consolidation** -- Processing financial data, including employee-related payroll and HR data, across multiple legal entities as directed by the Controller.
3. **Audit and compliance** -- Maintaining audit logs of user actions for security, accountability, and regulatory compliance purposes.
4. **Technical operations** -- Performing backups, applying security updates, monitoring system health, and ensuring availability.

The Processor shall process personal data only on documented instructions from the Controller, unless required to do so by applicable EU or Member State law.

---

## 4. Types of Personal Data Processed

| Category | Data Elements |
|----------|--------------|
| User account data | Email address, full name, user role, hashed password |
| Employee records | Employee name, email, position, salary data (gross, net, taxes, benefits) |
| Audit log data | IP address, user-agent string, timestamps, user ID, actions performed |
| Financial data | Data associated with legal entities, intercompany transactions, tax records |

---

## 5. Categories of Data Subjects

| Category | Description |
|----------|-------------|
| Users of the Service | Employees or agents of the Controller who are authorized to use ConsolidaSuite |
| Employees of client companies | Individuals whose HR/payroll data is processed through the platform on behalf of the Controller's subsidiary or affiliated entities |

---

## 6. Obligations of the Processor

The Processor shall:

1. Process personal data only on documented instructions from the Controller, including with regard to transfers of personal data to a third country, unless required by EU or Member State law (Art. 28(3)(a) GDPR).
2. Ensure that persons authorized to process personal data have committed themselves to confidentiality or are under an appropriate statutory obligation of confidentiality (Art. 28(3)(b) GDPR).
3. Implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk (Art. 28(3)(c) and Art. 32 GDPR). See Section 9.
4. Respect the conditions for engaging sub-processors as set out in Section 7 (Art. 28(3)(d) GDPR).
5. Assist the Controller, taking into account the nature of processing, with appropriate technical and organizational measures for the fulfillment of the Controller's obligation to respond to data subject requests (Art. 28(3)(e) GDPR).
6. Assist the Controller in ensuring compliance with obligations under Articles 32-36 GDPR, taking into account the nature of processing and the information available to the Processor (Art. 28(3)(f) GDPR).
7. At the choice of the Controller, delete or return all personal data after the end of the provision of services, and delete existing copies unless storage is required by law (Art. 28(3)(g) GDPR). See Section 11.
8. Make available to the Controller all information necessary to demonstrate compliance with Article 28 GDPR and allow for and contribute to audits (Art. 28(3)(h) GDPR). See Section 12.

---

## 7. Sub-processors

### 7.1 Authorized Sub-processors

The Controller provides general written authorization for the Processor to engage sub-processors. The following sub-processors are currently engaged:

| Sub-processor | Service | Location | Data Processed |
|--------------|---------|----------|---------------|
| Hetzner Online GmbH | Cloud hosting infrastructure | EU (Germany) | All application data stored and processed on Hetzner infrastructure |

### 7.2 Changes to Sub-processors

The Processor shall:

1. Inform the Controller of any intended addition or replacement of sub-processors, giving the Controller the opportunity to object to such changes.
2. Provide at least 30 days' advance written notice before engaging a new sub-processor.
3. If the Controller objects on reasonable grounds, the parties shall discuss in good faith. If no resolution is reached, the Controller may terminate the affected service.

### 7.3 Sub-processor Obligations

The Processor shall impose the same data protection obligations on sub-processors as set out in this DPA by way of a contract. The Processor remains fully liable to the Controller for the performance of the sub-processor's obligations.

---

## 8. Data Transfers

All personal data is processed exclusively within the European Union / European Economic Area (EU/EEA). No transfers of personal data to third countries are made.

If a transfer to a third country becomes necessary in the future, the Processor shall:

1. Inform the Controller in advance.
2. Ensure that appropriate safeguards are in place in accordance with Chapter V of the GDPR (e.g., Standard Contractual Clauses, adequacy decision).
3. Obtain the Controller's prior written consent.

---

## 9. Security Measures

The Processor implements the following technical and organizational measures (Art. 32 GDPR):

### 9.1 Technical Measures

| Measure | Description |
|---------|-------------|
| Encryption in transit | All data transmitted over TLS 1.2+ |
| Password hashing | Bcrypt with appropriate cost factor |
| Access control | Role-based access control (RBAC) enforced at application level |
| Authentication | JWT-based authentication with short-lived access tokens and HTTP-only cookies |
| Rate limiting | API rate limiting to prevent brute-force and abuse |
| Input validation | Server-side validation and sanitization of all user input |
| Backup encryption | Backups encrypted at rest |
| Network security | Firewall rules restricting access; no unnecessary ports exposed |

### 9.2 Organizational Measures

| Measure | Description |
|---------|-------------|
| Confidentiality | Staff with access to personal data are bound by confidentiality obligations |
| Access management | Principle of least privilege; access granted on a need-to-know basis |
| Audit logging | All significant actions are logged and logs are retained for 3 years |
| Incident response | Documented incident response plan with defined procedures and responsibilities |
| Regular review | Security measures are reviewed and updated periodically |

---

## 10. Data Breach Notification

### 10.1 Notification to Controller

In the event of a personal data breach, the Processor shall notify the Controller without undue delay and in any event within **72 hours** of becoming aware of the breach. The notification shall include:

1. Description of the nature of the breach, including the categories and approximate number of data subjects affected.
2. The name and contact details of the Processor's Data Protection Officer or other contact point.
3. A description of the likely consequences of the breach.
4. A description of the measures taken or proposed to address the breach, including measures to mitigate its possible adverse effects.

### 10.2 Cooperation

The Processor shall cooperate with the Controller and take reasonable steps to assist in the investigation, mitigation, and remediation of the breach. The Processor shall not inform any third party of the breach without the Controller's prior consent, except where required by law.

### 10.3 Documentation

The Processor shall document all data breaches, including the facts relating to the breach, its effects, and the remedial action taken.

---

## 11. Data Deletion and Return on Termination

### 11.1 Upon Termination

Upon termination of the service agreement, the Processor shall, at the Controller's choice:

1. **Return** all personal data to the Controller in a structured, commonly used, and machine-readable format; or
2. **Delete** all personal data and certify such deletion in writing.

### 11.2 Timeline

The Controller must communicate their choice within 30 days of termination. If no instruction is received within this period, the Processor shall delete all personal data.

### 11.3 Exceptions

The Processor may retain personal data to the extent required by applicable EU or Member State law, provided that the Processor ensures the confidentiality of such data and processes it only for the purpose required by law.

### 11.4 Backup Deletion

Copies of personal data in backup systems will be deleted in accordance with the backup retention schedule (maximum 30 days).

---

## 12. Audit Rights

### 12.1 Information and Audit

The Processor shall:

1. Make available to the Controller all information necessary to demonstrate compliance with the obligations laid down in Article 28 GDPR.
2. Allow for and contribute to audits, including inspections, conducted by the Controller or an auditor mandated by the Controller.

### 12.2 Conditions

Audits shall be:

1. Conducted with at least 30 days' written notice.
2. Performed during normal business hours.
3. Conducted in a manner that minimizes disruption to the Processor's operations.
4. Subject to reasonable confidentiality obligations.

### 12.3 Costs

The Controller shall bear the costs of any audit it initiates, unless the audit reveals material non-compliance by the Processor.

---

## 13. Liability

The parties' liability under this DPA shall be subject to the limitations and exclusions of liability set out in the underlying service agreement, except where prohibited by applicable law.

---

## 14. Governing Law

This DPA shall be governed by and construed in accordance with the laws of [JURISDICTION], and the parties submit to the exclusive jurisdiction of the courts of [JURISDICTION].

---

## 15. Signatures

| | Controller | Processor |
|--|-----------|-----------|
| **Organization** | [CLIENT ORGANIZATION NAME] | [COMPANY NAME] |
| **Name** | [AUTHORIZED REPRESENTATIVE NAME] | [AUTHORIZED REPRESENTATIVE NAME] |
| **Title** | [TITLE] | [TITLE] |
| **Date** | [DATE] | [DATE] |
| **Signature** | _________________________ | _________________________ |

---

*This Data Processing Agreement is effective as of the date of last signature above.*
