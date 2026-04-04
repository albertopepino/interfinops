# Incident Response Plan

**ConsolidaSuite** -- Financial Consolidation Platform

**Last Updated:** 2026-04-03

**Classification:** Internal -- Confidential

---

## 1. Purpose and Scope

This Incident Response Plan ("IRP") defines the procedures for detecting, responding to, and recovering from security incidents and personal data breaches affecting the ConsolidaSuite platform. It applies to all personnel involved in the development, operation, and administration of the Service.

This plan is designed to ensure compliance with:

- GDPR Art. 33 (notification to supervisory authority within 72 hours)
- GDPR Art. 34 (communication to data subjects when high risk)
- Art. 32 (security of processing)

---

## 2. Incident Severity Levels

| Level | Name | Description | Response Time | Examples |
|-------|------|-------------|---------------|----------|
| **P1** | Critical | Active data breach, service fully compromised, or large-scale unauthorized access to personal data | Immediate (within 1 hour) | Database exfiltration, complete service compromise, ransomware, unauthorized access to salary/financial data at scale |
| **P2** | High | Confirmed security incident with potential data exposure, or significant service degradation | Within 4 hours | Unauthorized access to a single account, vulnerability actively exploited, partial service outage affecting data integrity |
| **P3** | Medium | Suspected incident or vulnerability with no confirmed data exposure | Within 24 hours | Suspicious login patterns, unpatched vulnerability discovered, failed brute-force attempts at scale |
| **P4** | Low | Minor security event, no data exposure or service impact | Within 72 hours | Single failed login attempt, minor configuration issue, informational security alert |

---

## 3. Incident Response Phases

### Phase 1: Detection and Identification

**Objective:** Identify that an incident has occurred and classify its severity.

**Actions:**

1. Monitor audit logs, system alerts, and error reports for anomalies.
2. Receive and triage reports from users, team members, or external parties.
3. Verify that the event constitutes a genuine security incident (not a false positive).
4. Assign an initial severity level (P1--P4).
5. Designate an Incident Lead responsible for coordinating the response.
6. Open an incident record with timestamp, reporter, and initial assessment.

**Detection sources:**

- Application audit logs (user actions, authentication events)
- System monitoring and alerting
- Rate limiting alerts
- User reports (via [SUPPORT EMAIL ADDRESS])
- External vulnerability disclosures

---

### Phase 2: Containment

**Objective:** Limit the scope and impact of the incident.

**Immediate containment (P1/P2):**

1. Isolate affected systems or components if necessary.
2. Revoke compromised credentials or tokens.
3. Block suspicious IP addresses or accounts.
4. Disable affected functionality if it poses ongoing risk.
5. Preserve evidence (do not destroy logs or modify affected data).

**Short-term containment:**

1. Apply temporary fixes or workarounds.
2. Increase monitoring on affected and adjacent systems.
3. Ensure backup systems are unaffected.

---

### Phase 3: Assessment

**Objective:** Determine the full scope and impact of the incident.

**Assess:**

1. **What data was affected?** Identify the categories of personal data involved (user accounts, financial data, HR/payroll data, audit logs).
2. **How many data subjects are affected?** Determine the approximate number of individuals whose data was compromised.
3. **What was the nature of the breach?** Unauthorized access, data loss, data alteration, data disclosure, or system destruction.
4. **What is the severity of impact on data subjects?** Consider the sensitivity of the data (salary data is high sensitivity), the likelihood of harm, and the nature of potential consequences.
5. **Is the incident ongoing?** Confirm that containment is effective.
6. **Which clients/tenants are affected?** Identify affected organizations for notification.

**Document all findings in the incident record.**

---

### Phase 4: Notification

**Objective:** Fulfill legal notification obligations under GDPR.

#### 4.1 Notification to Supervisory Authority (Art. 33 GDPR)

**Deadline: Within 72 hours of becoming aware of a personal data breach.**

If the breach is likely to result in a risk to the rights and freedoms of natural persons, notify the competent supervisory authority. The notification shall include:

1. Nature of the personal data breach (categories and approximate number of data subjects and records).
2. Name and contact details of the DPO.
3. Likely consequences of the breach.
4. Measures taken or proposed to address the breach.

**Supervisory Authority Contact:**
- Authority: [SUPERVISORY AUTHORITY NAME]
- Address: [SUPERVISORY AUTHORITY ADDRESS]
- Online reporting: [SUPERVISORY AUTHORITY REPORTING URL]
- Phone: [SUPERVISORY AUTHORITY PHONE]

If full information is not available within 72 hours, provide initial notification with available details and supplement with additional information as it becomes available.

#### 4.2 Notification to Data Subjects (Art. 34 GDPR)

If the breach is likely to result in a **high risk** to the rights and freedoms of natural persons, communicate the breach to affected data subjects without undue delay.

**High-risk indicators for ConsolidaSuite:**
- Unauthorized disclosure of salary/compensation data
- Unauthorized access to financial records
- Compromise of authentication credentials (even if hashed)
- Large-scale unauthorized access to employee records

The communication to data subjects shall:
1. Describe the nature of the breach in clear and plain language.
2. Provide the DPO's contact details.
3. Describe the likely consequences.
4. Describe the measures taken to address the breach and mitigate harm.
5. Provide recommendations for the individual (e.g., password change).

#### 4.3 Notification to Affected Clients (Controllers)

As a Processor, [COMPANY NAME] shall notify affected client organizations (Controllers) without undue delay and within 72 hours, per the obligations in the Data Processing Agreement. The Controller is then responsible for their own Art. 33/34 notifications.

---

### Phase 5: Investigation and Root Cause Analysis

**Objective:** Determine how the incident occurred and identify the root cause.

**Actions:**

1. Collect and preserve all relevant evidence (logs, system snapshots, network captures).
2. Reconstruct the timeline of events.
3. Identify the attack vector or failure mode.
4. Determine whether existing controls failed or were bypassed.
5. Identify contributing factors (e.g., misconfiguration, unpatched vulnerability, human error).
6. Document the root cause and contributing factors.

---

### Phase 6: Remediation

**Objective:** Eliminate the root cause and restore normal operations.

**Actions:**

1. Apply permanent fixes to address the root cause (patches, configuration changes, code fixes).
2. Restore affected systems and data from backups if necessary.
3. Verify that the fix is effective and does not introduce new issues.
4. Restore normal service operations.
5. Re-enable any functionality that was disabled during containment.
6. Confirm with affected clients that the issue is resolved.

---

### Phase 7: Post-Incident Review

**Objective:** Learn from the incident and improve defenses.

**Actions (within 14 days of resolution):**

1. Conduct a post-incident review meeting with all involved personnel.
2. Document lessons learned.
3. Identify improvements to:
   - Technical controls (code, infrastructure, monitoring)
   - Organizational processes (response procedures, communication)
   - Documentation (this IRP, runbooks)
4. Create action items with owners and deadlines.
5. Update this Incident Response Plan if needed.
6. Share relevant (non-sensitive) findings with the team.

---

### Phase 8: Documentation

**Objective:** Maintain a complete record of the incident.

**The incident record must include:**

1. Incident identifier and classification (P1--P4).
2. Date and time of detection.
3. Date and time of containment.
4. Description of the incident.
5. Data categories and data subjects affected.
6. Assessment of impact and severity.
7. Actions taken at each phase.
8. Notifications made (supervisory authority, data subjects, clients) with dates.
9. Root cause analysis.
10. Remediation actions taken.
11. Lessons learned and follow-up actions.
12. Names of personnel involved in the response.

**Incident records are retained for a minimum of 5 years.**

---

## 4. Contact List

### Internal Contacts

| Role | Name | Email | Phone |
|------|------|-------|-------|
| Incident Lead (Primary) | [NAME] | [EMAIL] | [PHONE] |
| Incident Lead (Backup) | [NAME] | [EMAIL] | [PHONE] |
| Data Protection Officer | [NAME] | [DPO EMAIL ADDRESS] | [PHONE] |
| System Administrator | [NAME] | [EMAIL] | [PHONE] |
| Development Lead | [NAME] | [EMAIL] | [PHONE] |
| Management / Decision-maker | [NAME] | [EMAIL] | [PHONE] |

### External Contacts

| Organization | Purpose | Contact |
|-------------|---------|---------|
| [SUPERVISORY AUTHORITY NAME] | GDPR breach notification | [CONTACT DETAILS] |
| Hetzner Online GmbH | Infrastructure provider support | https://www.hetzner.com/support |
| [LEGAL COUNSEL] | Legal advice | [CONTACT DETAILS] |
| [CYBER INSURANCE PROVIDER] | Insurance notification | [CONTACT DETAILS] |

---

## 5. Communication Templates

### Template A: Initial Internal Alert

```
SUBJECT: [P1/P2/P3/P4] Security Incident - [Brief Description]

Severity: [P1/P2/P3/P4]
Detected: [Date/Time UTC]
Detected by: [Name/System]
Description: [Brief description of the incident]
Affected systems: [List]
Current status: [Detected / Contained / Under investigation]
Incident Lead: [Name]

Immediate actions required:
- [Action 1]
- [Action 2]

Next update: [Time]
```

### Template B: Supervisory Authority Notification (Art. 33)

```
SUBJECT: Personal Data Breach Notification - [COMPANY NAME] / ConsolidaSuite

1. Organization: [COMPANY NAME], [ADDRESS]
   DPO: [NAME], [EMAIL], [PHONE]

2. Nature of the breach:
   - Type: [unauthorized access / data loss / data disclosure / other]
   - Categories of data: [user accounts / financial data / HR data / audit logs]
   - Approximate number of data subjects: [number]
   - Approximate number of records: [number]

3. Likely consequences:
   [Description of potential impact on data subjects]

4. Measures taken:
   - Containment: [description]
   - Remediation: [description]
   - Mitigation for data subjects: [description]

5. Additional information:
   [Any supplementary details; note if further updates will follow]
```

### Template C: Data Subject Notification (Art. 34)

```
SUBJECT: Important Security Notice Regarding Your ConsolidaSuite Account

Dear [Name/User],

We are writing to inform you of a security incident that may have affected
your personal data.

WHAT HAPPENED:
[Clear, plain-language description of the incident]

WHAT DATA WAS AFFECTED:
[Specific categories of data that may have been exposed]

WHAT WE ARE DOING:
[Description of containment and remediation measures]

WHAT YOU SHOULD DO:
- [Recommended action 1, e.g., change your password]
- [Recommended action 2, e.g., monitor for suspicious activity]

CONTACT:
If you have questions, please contact our Data Protection Officer:
[DPO NAME], [DPO EMAIL ADDRESS]

You also have the right to lodge a complaint with [SUPERVISORY AUTHORITY NAME].

[COMPANY NAME]
```

### Template D: Client (Controller) Notification

```
SUBJECT: Data Processing Incident Notification - ConsolidaSuite

Dear [Client Contact],

In accordance with our Data Processing Agreement, we are notifying you of
a personal data breach affecting data processed on your behalf.

Incident detected: [Date/Time UTC]
Nature of breach: [Description]
Data affected: [Categories and approximate scope]
Your affected users/records: [Specifics for this client]

Measures taken:
- [Containment actions]
- [Remediation actions]

We recommend you assess whether notification to your supervisory authority
(Art. 33 GDPR) and/or affected data subjects (Art. 34 GDPR) is required.

We are available to assist with your notification obligations. Please contact:
[DPO NAME], [DPO EMAIL ADDRESS]

[COMPANY NAME]
```

---

## 6. Testing and Review

This Incident Response Plan shall be:

- **Reviewed** at least annually or after any significant incident.
- **Tested** through tabletop exercises at least once per year.
- **Updated** whenever material changes to the platform, infrastructure, or team occur.

| Date | Activity | Participants | Findings |
|------|----------|-------------|----------|
| [DATE] | [Initial plan creation / Annual review / Tabletop exercise] | [NAMES] | [FINDINGS] |

---

*This document is maintained by [DPO NAME], Data Protection Officer, and approved by [MANAGEMENT APPROVER NAME].*
