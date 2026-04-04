# Data Protection Impact Assessment

## HR/Payroll Consolidation Module

**ConsolidaSuite** -- Financial Consolidation Platform

**Last Updated:** 2026-04-03

**Assessment Conducted By:** [DPO NAME / ASSESSMENT TEAM]

**Approved By:** [MANAGEMENT APPROVER NAME]

---

## 1. Introduction

This Data Protection Impact Assessment ("DPIA") is conducted pursuant to Article 35 of the GDPR for the HR/Payroll consolidation module of ConsolidaSuite. The assessment evaluates the risks to the rights and freedoms of data subjects arising from the processing of employee personal data, including salary information, and documents the measures implemented to mitigate those risks.

A DPIA is warranted because the processing involves:

- Sensitive financial data (salary, tax, and benefits information) at scale.
- Data about employees who are not direct users of the platform and may not be fully aware of the processing.
- Consolidation of data across multiple legal entities, creating a centralized view of employee compensation.

---

## 2. Description of Processing

### 2.1 What Is Processed

| Data Element | Description |
|-------------|-------------|
| Employee name | Full name of the employee |
| Employee email | Work email address |
| Position / title | Job title and role within the organization |
| Gross salary | Total compensation before deductions |
| Net salary | Take-home pay after deductions |
| Tax withholdings | Income tax, social security contributions, and other statutory deductions |
| Benefits | Health insurance, pension contributions, and other benefits |
| Entity assignment | Which legal entity employs the individual |

### 2.2 How It Is Processed

1. Client organizations (Controllers) upload or input HR/payroll data into ConsolidaSuite for each of their subsidiary entities.
2. The platform stores this data in a multi-tenant database, with strict tenant isolation.
3. Data is consolidated across entities for reporting purposes (headcount, total compensation costs, entity-level summaries).
4. Consolidated views are accessible only to users with appropriate roles (admin, group CFO).
5. Site-level users can only see data for their own entity.
6. All access to HR/payroll data is recorded in the audit log.

### 2.3 Who Is Involved

| Party | Role |
|-------|------|
| Client organization | Data Controller -- determines purposes and means of processing |
| [COMPANY NAME] | Data Processor -- processes data on behalf of the Controller |
| Hetzner Online GmbH | Sub-processor -- provides hosting infrastructure |

### 2.4 Data Subjects

Employees of client organizations and their subsidiary entities. These individuals are typically not direct users of ConsolidaSuite and may not interact with the platform.

### 2.5 Scale of Processing

The platform is designed to handle multi-entity group structures. A typical deployment may involve:

- Multiple legal entities per client organization
- Hundreds to thousands of employee records per entity
- Monthly or periodic data updates (payroll cycles)

---

## 3. Necessity and Proportionality Assessment

### 3.1 Necessity

| Question | Assessment |
|----------|-----------|
| Is the processing necessary for the stated purpose? | **Yes.** Financial consolidation requires aggregating HR/payroll data across entities to produce consolidated financial reports, which is a legal and business requirement for group companies. |
| Could the purpose be achieved with less data? | **Partially.** Aggregated/anonymized data could serve some reporting needs, but entity-level and individual-level data is necessary for accurate financial consolidation, intercompany cost allocation, and statutory reporting. |
| Is the processing proportionate to the purpose? | **Yes.** Only data elements directly relevant to payroll consolidation are collected. No unnecessary personal data (e.g., home addresses, personal phone numbers, health records beyond benefits enrollment) is processed. |

### 3.2 Proportionality

- **Data minimization:** Only payroll-relevant data fields are collected. The system does not request or store personal data beyond what is necessary for consolidation.
- **Purpose limitation:** HR/payroll data is processed solely for consolidation reporting. It is not used for performance evaluation, profiling, or any purpose unrelated to financial consolidation.
- **Storage limitation:** Data is retained for 7 years in line with financial record retention obligations, after which it is deleted.
- **Accuracy:** The Controller is responsible for ensuring data accuracy. The system supports data correction workflows.

---

## 4. Risk Assessment

### 4.1 Identified Risks

| # | Risk | Likelihood | Severity | Overall Risk | Description |
|---|------|-----------|----------|-------------|-------------|
| R1 | Unauthorized disclosure of salary data | Low | High | **Medium** | An unauthorized user gains access to salary information, leading to workplace conflict, discrimination, or reputational harm to affected employees. |
| R2 | Unauthorized access to consolidated HR data | Low | High | **Medium** | A user at one entity accesses employee data from another entity, violating data boundaries. |
| R3 | Data breach via infrastructure compromise | Low | High | **Medium** | An attacker compromises the hosting infrastructure and exfiltrates HR/payroll data. |
| R4 | Insider threat / privilege abuse | Low | Medium | **Low-Medium** | An authorized admin user accesses salary data without a legitimate business need. |
| R5 | Inaccurate data leading to incorrect decisions | Low | Medium | **Low** | Incorrect payroll data leads to erroneous financial reports or decisions affecting employees. |
| R6 | Failure to delete data upon termination | Low | Low | **Low** | Data is retained beyond the agreed period or not deleted when the service agreement ends. |

### 4.2 Risk to Data Subjects

Salary and compensation data is among the most sensitive categories of employee information. Unauthorized disclosure could result in:

- **Discrimination:** Salary disparities becoming known could lead to workplace discrimination or targeted treatment.
- **Financial harm:** Knowledge of an individual's salary could be exploited for social engineering, fraud, or extortion.
- **Psychological distress:** Employees may experience distress if their compensation details are disclosed to colleagues or third parties.
- **Employment consequences:** In some contexts, disclosure of salary data could affect employment relationships or negotiations.

---

## 5. Mitigating Measures

### 5.1 Technical Measures

| Measure | Risk(s) Addressed | Description |
|---------|-------------------|-------------|
| **Role-Based Access Control (RBAC)** | R1, R2, R4 | Strict role-based permissions ensure that only users with the `admin` or `group_cfo` role can access consolidated HR/payroll data. Site-level users can only view data for their assigned entity. |
| **Site-level data isolation** | R2 | The application enforces entity-level data boundaries. Users assigned to a specific site/entity cannot query or view data from other entities, even through the API. |
| **Encryption in transit** | R3 | All data transmitted between the client browser and the server is encrypted using TLS 1.2+. |
| **Audit logging** | R1, R2, R4 | All access to HR/payroll data is logged with user ID, timestamp, IP address, action, and resource. Logs are retained for 3 years and are available for review. |
| **Authentication security** | R1, R3 | JWT-based authentication with short-lived access tokens (15 min), HTTP-only Secure cookies, bcrypt password hashing, and rate limiting on login endpoints. |
| **Rate limiting** | R3 | API rate limiting prevents brute-force attacks and automated data extraction. |
| **Input validation** | R5 | Server-side validation ensures data integrity and prevents injection attacks. |
| **Backup security** | R3, R6 | Backups are encrypted and automatically deleted after 30 days on a rolling basis. |

### 5.2 Organizational Measures

| Measure | Risk(s) Addressed | Description |
|---------|-------------------|-------------|
| **Principle of least privilege** | R1, R2, R4 | Users are granted the minimum permissions necessary for their role. Role assignment is controlled by organization administrators. |
| **Data Processing Agreement** | R3, R6 | A DPA is in place with Hetzner (sub-processor) and offered to all client organizations (Controllers). |
| **Incident response plan** | R1, R2, R3 | A documented incident response plan with 72-hour notification commitment ensures timely response to any breach. |
| **Data retention policy** | R6 | Clear retention periods are defined and enforced. Data is deleted 30 days after account/service termination. |
| **Staff confidentiality** | R4 | Personnel with access to production systems are bound by confidentiality obligations. |
| **Controller responsibility** | R5 | The Controller is responsible for data accuracy. ConsolidaSuite provides tools for data review and correction. |

---

## 6. Residual Risk Assessment

After implementation of all mitigating measures:

| # | Risk | Initial Risk | Mitigating Measures | Residual Risk |
|---|------|-------------|---------------------|---------------|
| R1 | Unauthorized salary disclosure | Medium | RBAC, site isolation, audit logging, authentication | **Low** |
| R2 | Cross-entity unauthorized access | Medium | Site-level isolation, RBAC, audit logging | **Low** |
| R3 | Infrastructure breach | Medium | TLS, DPA with Hetzner, incident response, backup encryption | **Low** |
| R4 | Insider privilege abuse | Low-Medium | Audit logging, least privilege, RBAC | **Low** |
| R5 | Inaccurate data | Low | Input validation, Controller responsibility | **Low** |
| R6 | Failure to delete data | Low | Retention policy, DPA obligations, automated backup deletion | **Low** |

---

## 7. Conclusion

The residual risks to data subjects are assessed as **acceptable** given the implemented technical and organizational controls. The processing is necessary and proportionate for the legitimate purpose of multi-entity financial consolidation.

**Key safeguards:**

- RBAC ensures salary data is only accessible to authorized roles (admin, group CFO).
- Site-level isolation prevents cross-entity data leakage.
- Comprehensive audit logging provides accountability and supports investigation of any access concerns.
- Encryption in transit protects data during transmission.
- The incident response plan ensures timely breach notification per GDPR requirements.

**Recommendation:** Proceed with processing. Review this DPIA annually or when significant changes are made to the HR/payroll module.

---

## 8. Consultation

| Question | Response |
|----------|----------|
| Was the DPO consulted? | Yes -- [DPO NAME], [DATE] |
| Was prior consultation with the supervisory authority required (Art. 36)? | No -- residual risk is not considered high after mitigating measures |
| Were data subjects or their representatives consulted? | [YES/NO -- DESCRIBE IF YES] |

---

## 9. Review Schedule

| Date | Reviewer | Outcome |
|------|----------|---------|
| 2026-04-03 | [DPO NAME] | Initial DPIA completed |
| [NEXT REVIEW DATE] | [REVIEWER] | [PENDING] |

This DPIA shall be reviewed:

- At least **annually**.
- When **significant changes** are made to the HR/payroll module (new data elements, new processing activities, new sub-processors).
- When a **data breach** affects HR/payroll data.

---

*Assessment conducted by [DPO NAME] and approved by [MANAGEMENT APPROVER NAME] on 2026-04-03.*
