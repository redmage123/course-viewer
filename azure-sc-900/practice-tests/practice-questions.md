# SC-900 Practice Questions

## Instructions
These practice questions help prepare for the SC-900 exam. Answer each question before checking the solution.

---

## Section 1: Security, Compliance, and Identity Concepts (10-15%)

### Question 1
Which security principle ensures data has not been modified or tampered with?

A) Confidentiality
B) Integrity
C) Availability
D) Non-repudiation

<details>
<summary>Show Answer</summary>

**Answer: B) Integrity**

Explanation: Integrity ensures data hasn't been modified. Confidentiality protects access. Availability ensures systems are accessible.
</details>

---

### Question 2
Which Zero Trust principle states that users should have only the minimum permissions needed?

A) Verify explicitly
B) Assume breach
C) Least privilege access
D) Defense in depth

<details>
<summary>Show Answer</summary>

**Answer: C) Least privilege access**

Explanation: Least privilege access limits user permissions using just-in-time (JIT) and just-enough-access (JEA).
</details>

---

### Question 3
In the shared responsibility model, which is ALWAYS the customer's responsibility?

A) Physical datacenter security
B) Data classification
C) Network infrastructure
D) Physical host maintenance

<details>
<summary>Show Answer</summary>

**Answer: B) Data classification**

Explanation: Data classification and accountability is always the customer's responsibility regardless of cloud service type.
</details>

---

## Section 2: Microsoft Entra (25-30%)

### Question 4
What is the term for proving your identity (who you are)?

A) Authorization
B) Authentication
C) Federation
D) Delegation

<details>
<summary>Show Answer</summary>

**Answer: B) Authentication**

Explanation: Authentication (AuthN) proves who you are. Authorization (AuthZ) determines what you can do.
</details>

---

### Question 5
Which authentication method uses multiple factors to verify identity?

A) SSO
B) MFA
C) Passwordless
D) Federation

<details>
<summary>Show Answer</summary>

**Answer: B) MFA**

Explanation: Multi-Factor Authentication requires multiple factors (something you know, have, or are).
</details>

---

### Question 6
Conditional Access policies use which approach to make access decisions?

A) Always allow, then audit
B) IF-THEN logic based on signals
C) Block all unknown users
D) Time-based access only

<details>
<summary>Show Answer</summary>

**Answer: B) IF-THEN logic based on signals**

Explanation: Conditional Access uses IF (conditions/signals) THEN (access decision) logic.
</details>

---

### Question 7
Which type of risk in Entra ID Protection indicates that a sign-in might be unauthorized?

A) User risk
B) Sign-in risk
C) Application risk
D) Device risk

<details>
<summary>Show Answer</summary>

**Answer: B) Sign-in risk**

Explanation: Sign-in risk indicates the probability that a specific sign-in is not authorized by the identity owner.
</details>

---

### Question 8
Which identity type is automatically managed by Azure for service-to-service authentication?

A) User identity
B) Service principal
C) Managed identity
D) Device identity

<details>
<summary>Show Answer</summary>

**Answer: C) Managed identity**

Explanation: Managed identities are automatically managed by Azure, eliminating the need to manage credentials.
</details>

---

## Section 3: Microsoft Security Solutions (35-40%)

### Question 9
Which service provides Cloud Security Posture Management (CSPM) for Azure?

A) Microsoft Sentinel
B) Microsoft Defender for Cloud
C) Microsoft Defender for Endpoint
D) Azure Firewall

<details>
<summary>Show Answer</summary>

**Answer: B) Microsoft Defender for Cloud**

Explanation: Defender for Cloud provides CSPM with Secure Score, recommendations, and compliance tracking.
</details>

---

### Question 10
What does a higher Secure Score in Microsoft Defender for Cloud indicate?

A) More security alerts
B) Better security posture
C) More resources deployed
D) Higher costs

<details>
<summary>Show Answer</summary>

**Answer: B) Better security posture**

Explanation: A higher Secure Score indicates better security posture and more security recommendations implemented.
</details>

---

### Question 11
Which Microsoft Defender XDR product protects endpoints (devices)?

A) Defender for Office 365
B) Defender for Identity
C) Defender for Endpoint
D) Defender for Cloud Apps

<details>
<summary>Show Answer</summary>

**Answer: C) Defender for Endpoint**

Explanation: Defender for Endpoint protects devices including Windows, Mac, Linux, and mobile.
</details>

---

### Question 12
Microsoft Sentinel is a cloud-native solution that provides which capabilities?

A) Endpoint protection only
B) Email security only
C) SIEM and SOAR
D) Identity management

<details>
<summary>Show Answer</summary>

**Answer: C) SIEM and SOAR**

Explanation: Sentinel is a SIEM (Security Information and Event Management) and SOAR (Security Orchestration, Automation, Response) solution.
</details>

---

### Question 13
Which Azure service provides secure RDP/SSH access to VMs without exposing public IPs?

A) Azure Firewall
B) Azure Bastion
C) VPN Gateway
D) ExpressRoute

<details>
<summary>Show Answer</summary>

**Answer: B) Azure Bastion**

Explanation: Azure Bastion provides secure RDP/SSH connectivity through the Azure portal over TLS.
</details>

---

### Question 14
Which Defender product protects SaaS applications and provides CASB functionality?

A) Defender for Endpoint
B) Defender for Identity
C) Defender for Office 365
D) Defender for Cloud Apps

<details>
<summary>Show Answer</summary>

**Answer: D) Defender for Cloud Apps**

Explanation: Defender for Cloud Apps is a CASB (Cloud Access Security Broker) that protects SaaS applications.
</details>

---

## Section 4: Microsoft Compliance Solutions (20-25%)

### Question 15
Which Microsoft Purview feature provides a risk-based score measuring compliance progress?

A) Information Protection
B) Compliance Manager
C) eDiscovery
D) Insider Risk Management

<details>
<summary>Show Answer</summary>

**Answer: B) Compliance Manager**

Explanation: Compliance Manager provides a Compliance Score that measures progress toward meeting compliance requirements.
</details>

---

### Question 16
Sensitivity labels in Microsoft Purview can do which of the following?

A) Encrypt content
B) Add watermarks
C) Restrict access
D) All of the above

<details>
<summary>Show Answer</summary>

**Answer: D) All of the above**

Explanation: Sensitivity labels can encrypt, add watermarks, restrict access, and apply other protections.
</details>

---

### Question 17
Which solution helps detect potential insider threats like data theft by departing employees?

A) Compliance Manager
B) DLP
C) Insider Risk Management
D) eDiscovery

<details>
<summary>Show Answer</summary>

**Answer: C) Insider Risk Management**

Explanation: Insider Risk Management detects internal threats including data theft, leaks, and policy violations.
</details>

---

### Question 18
Where can you find Microsoft's audit reports and compliance certifications?

A) Compliance Manager
B) Microsoft Purview portal
C) Service Trust Portal
D) Azure Portal

<details>
<summary>Show Answer</summary>

**Answer: C) Service Trust Portal**

Explanation: The Service Trust Portal (servicetrust.microsoft.com) provides audit reports and compliance documentation.
</details>

---

### Question 19
What is the purpose of DLP (Data Loss Prevention) policies?

A) Encrypt all data
B) Prevent sensitive data from leaving the organization
C) Detect malware
D) Manage user identities

<details>
<summary>Show Answer</summary>

**Answer: B) Prevent sensitive data from leaving the organization**

Explanation: DLP policies identify and prevent the sharing of sensitive information outside the organization.
</details>

---

### Question 20
Which eDiscovery tier provides advanced analytics and custodian management?

A) Content Search
B) eDiscovery Standard
C) eDiscovery Premium
D) Audit Premium

<details>
<summary>Show Answer</summary>

**Answer: C) eDiscovery Premium**

Explanation: eDiscovery Premium includes advanced analytics, custodian management, and additional capabilities.
</details>

---

## Section 5: Mixed Topics

### Question 21
What does XDR stand for?

A) Extended Data Recovery
B) Extended Detection and Response
C) External Defense and Recovery
D) Extreme Data Replication

<details>
<summary>Show Answer</summary>

**Answer: B) Extended Detection and Response**

Explanation: XDR (Extended Detection and Response) provides unified threat detection across multiple domains.
</details>

---

### Question 22
Which of the following is NOT a Zero Trust principle?

A) Verify explicitly
B) Least privilege access
C) Trust but verify
D) Assume breach

<details>
<summary>Show Answer</summary>

**Answer: C) Trust but verify**

Explanation: "Trust but verify" is the opposite of Zero Trust. The principle is "Never trust, always verify."
</details>

---

### Question 23
Legal Hold in eDiscovery is used to:

A) Delete old content automatically
B) Preserve content in-place during investigations
C) Encrypt sensitive documents
D) Block user access

<details>
<summary>Show Answer</summary>

**Answer: B) Preserve content in-place during investigations**

Explanation: Legal Hold preserves content to prevent deletion during legal or compliance investigations.
</details>

---

### Question 24
Which portal is used for Microsoft Defender XDR?

A) portal.azure.com
B) security.microsoft.com
C) compliance.microsoft.com
D) admin.microsoft.com

<details>
<summary>Show Answer</summary>

**Answer: B) security.microsoft.com**

Explanation: The Microsoft Defender portal at security.microsoft.com is the unified portal for Defender XDR.
</details>

---

### Question 25
Which Defense in Depth layer includes DDoS protection and firewalls?

A) Physical
B) Identity & Access
C) Perimeter
D) Network

<details>
<summary>Show Answer</summary>

**Answer: C) Perimeter**

Explanation: The Perimeter layer includes DDoS protection and perimeter firewalls to protect against external attacks.
</details>

---

## Scoring Guide

- 20-25 correct: Excellent! You're well-prepared for the exam.
- 15-19 correct: Good foundation, review weak areas.
- 10-14 correct: Need more study time, focus on core concepts.
- Below 10: Review all course materials before attempting the exam.

---

## Additional Practice

For more practice questions:
- [Microsoft Learn Practice Assessment](https://learn.microsoft.com/en-us/credentials/certifications/security-compliance-and-identity-fundamentals/practice/assessment)
- [SC-900 Exam Page](https://learn.microsoft.com/en-us/credentials/certifications/exams/sc-900/)
