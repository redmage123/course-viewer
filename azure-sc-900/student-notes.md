# SC-900: Security, Compliance, and Identity Fundamentals - Student Notes

## Course Overview

This 3-day certification prep course covers all domains tested on the Microsoft Security, Compliance, and Identity Fundamentals (SC-900) exam.

**Exam Details:**
- Cost: $165 USD
- Questions: 40-60
- Passing Score: 700/1000
- Duration: 180 minutes

---

## Day 1: Security, Compliance & Identity Concepts + Microsoft Entra

### CIA Triad

| Principle | Description | Controls |
|-----------|-------------|----------|
| **Confidentiality** | Only authorized access | Encryption, access controls |
| **Integrity** | Data not tampered | Hashing, digital signatures |
| **Availability** | Systems accessible | Redundancy, DDoS protection |

### Shared Responsibility Model

**Customer ALWAYS responsible for:**
- Data classification
- Account and identity management
- Device security (endpoints)

**Microsoft ALWAYS responsible for:**
- Physical datacenters
- Physical network
- Physical hosts

### Zero Trust Model

**"Never Trust, Always Verify"**

Three Principles:
1. **Verify explicitly** - Always authenticate using all data points
2. **Least privilege access** - JIT/JEA, minimum permissions
3. **Assume breach** - Minimize blast radius, segment access

Six Pillars: Identities, Devices, Applications, Data, Infrastructure, Networks

### Defense in Depth

Layers (outside to inside):
1. Physical Security
2. Identity & Access
3. Perimeter
4. Network
5. Compute
6. Application
7. Data

### Identity Concepts

**Authentication (AuthN):** Proving who you are
**Authorization (AuthZ):** What you can do

Identity is the new security perimeter in cloud environments.

### Microsoft Entra ID

Formerly Azure Active Directory - cloud identity service.

**Identity Types:**
- User: People in organization
- Service Principal: App identities
- Managed Identity: Auto-managed for Azure services
- Device: Registered/joined devices
- External: Guests and B2B users

### Authentication Methods

| Method | Description |
|--------|-------------|
| Password | Traditional, weakest |
| MFA | Multiple factors required |
| Passwordless | FIDO2, Windows Hello, Authenticator |
| SSO | One login for all apps |

**MFA Factors:**
- Something you know (password)
- Something you have (phone)
- Something you are (biometrics)

### Conditional Access

IF (conditions) THEN (access decision)

**Signals (Conditions):**
- User or group
- Location
- Device state
- Application
- Risk level
- Device platform

**Decisions:**
- Block access
- Grant access (with MFA, compliant device, etc.)
- Session controls

### Entra ID Protection

| Risk Type | Description |
|-----------|-------------|
| **User Risk** | Identity may be compromised |
| **Sign-in Risk** | Sign-in may be unauthorized |

Risk Levels: Low, Medium, High

Self-remediation: Users can reset passwords or complete MFA.

---

## Day 2: Microsoft Security Solutions

### Microsoft Defender for Cloud

Cloud Security Posture Management (CSPM) + Cloud Workload Protection (CWPP)

**Key Features:**
- Secure Score: Security posture percentage
- Recommendations: Hardening guidance
- Regulatory Compliance: Standards tracking
- Threat Protection: Workload-specific

**Defender Plans:**
- Defender for Servers, Storage, SQL, Containers, App Service, Key Vault, etc.

### Azure Network Security

| Service | Purpose |
|---------|---------|
| **Azure Firewall** | Managed cloud firewall |
| **DDoS Protection** | Attack mitigation |
| **NSGs** | Network traffic filtering |
| **Azure Bastion** | Secure RDP/SSH without public IP |

### Microsoft Defender XDR

Extended Detection and Response - unified security.

| Product | Protects |
|---------|----------|
| **Defender for Endpoint** | Devices |
| **Defender for Office 365** | Email and collaboration |
| **Defender for Identity** | On-prem Active Directory |
| **Defender for Cloud Apps** | SaaS applications (CASB) |

**Portal:** security.microsoft.com

### Microsoft Sentinel

Cloud-native SIEM + SOAR

**SIEM:** Security Information and Event Management
**SOAR:** Security Orchestration, Automation, Response

**Capabilities:**
- Collect: Data from all sources
- Detect: Analytics-based threat detection
- Investigate: AI-powered hunting
- Respond: Automated playbooks

**Key Features:**
- Data Connectors
- Workbooks (dashboards)
- Analytics Rules
- Incidents
- Playbooks (Logic Apps)
- Hunting queries

---

## Day 3: Microsoft Compliance Solutions

### Microsoft Purview

Unified compliance and data governance platform.

**Compliance Solutions:**
- Compliance Manager
- Information Protection
- Data Loss Prevention
- Insider Risk Management
- eDiscovery
- Audit

**Data Governance:**
- Data Map
- Data Catalog
- Data Estate Insights

### Compliance Manager

**Compliance Score:** Risk-based measurement of compliance progress

**Controls:**
- Microsoft-managed
- Customer-managed
- Shared

**Assessments:** Pre-built templates (GDPR, ISO 27001, HIPAA, etc.)

### Information Protection

**Know Your Data:**
- Sensitive info types
- Trainable classifiers
- Content/Activity explorer

**Protect Your Data:**
- Sensitivity labels
- Encryption
- Content marking
- Access restrictions

**Prevent Data Loss:**
- DLP policies
- Endpoint DLP
- Policy tips

### Insider Risk Management

Detect internal threats:
- Data theft (departing employees)
- Data leaks (accidental sharing)
- Security policy violations
- Offensive behavior

**Communication Compliance:** Monitor Teams, Exchange, etc.

### eDiscovery & Audit

**eDiscovery:**
- Content Search
- eDiscovery Standard (case management)
- eDiscovery Premium (advanced analytics)

**Audit:**
- Audit Standard: 180-day retention
- Audit Premium: 1-year retention

**Legal Hold:** Preserve content in-place

### Service Trust Portal

URL: servicetrust.microsoft.com

**Contains:**
- Audit reports (ISO, SOC, FedRAMP)
- Compliance guides
- Trust documents
- Regional resources

### Microsoft Privacy Principles

1. Control
2. Transparency
3. Security
4. Legal Protection
5. No Content-Based Targeting
6. Benefits to You

---

## Key Terms Quick Reference

| Term | Definition |
|------|------------|
| CIA | Confidentiality, Integrity, Availability |
| Zero Trust | Never trust, always verify |
| AuthN | Authentication (who you are) |
| AuthZ | Authorization (what you can do) |
| MFA | Multi-Factor Authentication |
| SSO | Single Sign-On |
| CSPM | Cloud Security Posture Management |
| CWPP | Cloud Workload Protection Platform |
| XDR | Extended Detection and Response |
| SIEM | Security Information and Event Management |
| SOAR | Security Orchestration, Automation, Response |
| CASB | Cloud Access Security Broker |
| DLP | Data Loss Prevention |
| PII | Personally Identifiable Information |

---

## Product Quick Reference

| Need | Product |
|------|---------|
| Cloud identity | Microsoft Entra ID |
| Access policies | Conditional Access |
| Risk-based auth | Entra ID Protection |
| Cloud security posture | Defender for Cloud |
| Endpoint protection | Defender for Endpoint |
| Email protection | Defender for Office 365 |
| On-prem AD protection | Defender for Identity |
| SaaS app security | Defender for Cloud Apps |
| SIEM/SOAR | Microsoft Sentinel |
| Compliance assessment | Compliance Manager |
| Data classification | Information Protection |
| Prevent data leaks | DLP |
| Internal threats | Insider Risk Management |
| Legal discovery | eDiscovery |
| Activity tracking | Audit |

---

## Exam Tips

1. **Know Zero Trust:** Three principles, six pillars
2. **Understand Defense in Depth:** All seven layers
3. **Differentiate products:**
   - Defender for Cloud = Azure security posture
   - Defender XDR = Cross-domain threat protection
   - Sentinel = SIEM/SOAR
4. **Know portals:**
   - security.microsoft.com = Defender
   - compliance.microsoft.com = Purview
   - servicetrust.microsoft.com = Trust/audit reports
5. **Conditional Access:** Know signals and decisions

---

## Additional Resources

- [Microsoft Learn SC-900 Path](https://learn.microsoft.com/en-us/credentials/certifications/security-compliance-and-identity-fundamentals/)
- [SC-900 Study Guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-900)
- [Practice Assessment](https://learn.microsoft.com/en-us/credentials/certifications/security-compliance-and-identity-fundamentals/practice/assessment)
