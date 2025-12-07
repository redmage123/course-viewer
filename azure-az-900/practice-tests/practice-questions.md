# Azure AZ-900 Practice Questions

## Instructions
These practice questions help prepare for the AZ-900 exam. Answer each question before checking the solution.

---

## Section 1: Cloud Concepts (25-30%)

### Question 1
Which cloud service model provides the MOST control over the underlying infrastructure?

A) SaaS
B) PaaS
C) IaaS
D) FaaS

<details>
<summary>Show Answer</summary>

**Answer: C) IaaS**

Explanation: IaaS (Infrastructure as a Service) provides the most control, allowing you to manage the OS, applications, and data while the provider manages the physical hardware.
</details>

---

### Question 2
Your company wants to keep sensitive data on-premises but use the cloud for burst capacity during peak periods. Which cloud model should you use?

A) Public cloud
B) Private cloud
C) Hybrid cloud
D) Community cloud

<details>
<summary>Show Answer</summary>

**Answer: C) Hybrid cloud**

Explanation: Hybrid cloud combines on-premises (private) with public cloud, allowing you to keep sensitive data locally while using cloud for additional capacity.
</details>

---

### Question 3
Which characteristic of cloud computing allows you to quickly deploy resources as demand increases?

A) High availability
B) Elasticity
C) Disaster recovery
D) Fault tolerance

<details>
<summary>Show Answer</summary>

**Answer: B) Elasticity**

Explanation: Elasticity is the ability to automatically scale resources up or down based on demand.
</details>

---

### Question 4
Moving from on-premises infrastructure to cloud computing shifts costs from:

A) OpEx to CapEx
B) CapEx to OpEx
C) Fixed to variable expenses
D) Both B and C

<details>
<summary>Show Answer</summary>

**Answer: D) Both B and C**

Explanation: Cloud computing shifts from upfront capital expenditure (CapEx) to ongoing operational expenditure (OpEx), and from fixed to variable costs based on usage.
</details>

---

### Question 5
In the shared responsibility model, who is ALWAYS responsible for data classification regardless of cloud service type?

A) Cloud provider
B) Customer
C) Shared responsibility
D) Third-party auditor

<details>
<summary>Show Answer</summary>

**Answer: B) Customer**

Explanation: Data classification and accountability is always the customer's responsibility, regardless of whether using IaaS, PaaS, or SaaS.
</details>

---

## Section 2: Azure Architecture (35-40%)

### Question 6
What is the minimum number of availability zones in an Azure region that supports them?

A) 1
B) 2
C) 3
D) 5

<details>
<summary>Show Answer</summary>

**Answer: C) 3**

Explanation: Azure regions that support availability zones have a minimum of 3 physically separate zones.
</details>

---

### Question 7
You need to host a web application without managing the underlying infrastructure or OS. Which service should you use?

A) Azure Virtual Machines
B) Azure App Service
C) Azure Container Instances
D) Azure Virtual Machine Scale Sets

<details>
<summary>Show Answer</summary>

**Answer: B) Azure App Service**

Explanation: App Service is a PaaS offering for hosting web apps without managing infrastructure or OS.
</details>

---

### Question 8
Which Azure service provides a private, dedicated connection to Azure that doesn't traverse the public internet?

A) VPN Gateway
B) Azure Load Balancer
C) ExpressRoute
D) Azure Firewall

<details>
<summary>Show Answer</summary>

**Answer: C) ExpressRoute**

Explanation: ExpressRoute provides a private connection to Azure through a connectivity provider, not over the public internet.
</details>

---

### Question 9
You need to store large amounts of unstructured data like images and videos. Which Azure storage service should you use?

A) Azure Files
B) Azure Blob Storage
C) Azure Table Storage
D) Azure Queue Storage

<details>
<summary>Show Answer</summary>

**Answer: B) Azure Blob Storage**

Explanation: Blob Storage is optimized for storing large amounts of unstructured data like images, videos, and documents.
</details>

---

### Question 10
Which storage redundancy option provides the highest durability by replicating data across two Azure regions?

A) LRS (Locally Redundant Storage)
B) ZRS (Zone-Redundant Storage)
C) GRS (Geo-Redundant Storage)
D) None of the above

<details>
<summary>Show Answer</summary>

**Answer: C) GRS (Geo-Redundant Storage)**

Explanation: GRS replicates data to a secondary region, providing 6 copies across 2 regions for maximum durability.
</details>

---

### Question 11
Which Azure database service is globally distributed and supports multiple data models?

A) Azure SQL Database
B) Azure Cosmos DB
C) Azure Database for MySQL
D) Azure Database for PostgreSQL

<details>
<summary>Show Answer</summary>

**Answer: B) Azure Cosmos DB**

Explanation: Cosmos DB is a globally distributed, multi-model NoSQL database with single-digit millisecond latency.
</details>

---

### Question 12
What is the name of Microsoft's cloud-based identity and access management service?

A) Active Directory Domain Services
B) Microsoft Entra ID
C) Azure Security Center
D) Azure Key Vault

<details>
<summary>Show Answer</summary>

**Answer: B) Microsoft Entra ID**

Explanation: Microsoft Entra ID (formerly Azure Active Directory) is the cloud-based identity service for authentication and authorization.
</details>

---

## Section 3: Management & Governance (30-35%)

### Question 13
Which Azure tool would you use to estimate costs BEFORE deploying resources?

A) Azure Cost Management
B) Azure Advisor
C) Azure Pricing Calculator
D) TCO Calculator

<details>
<summary>Show Answer</summary>

**Answer: C) Azure Pricing Calculator**

Explanation: The Pricing Calculator estimates costs before deployment. Cost Management monitors actual spending after deployment.
</details>

---

### Question 14
You want to prevent any user, including Owners, from accidentally deleting a critical production resource. What should you use?

A) RBAC
B) Azure Policy
C) Resource Lock
D) Management Group

<details>
<summary>Show Answer</summary>

**Answer: C) Resource Lock**

Explanation: Resource locks (CanNotDelete or ReadOnly) prevent changes even for users with Owner permissions.
</details>

---

### Question 15
What is the correct hierarchy of Azure management from broadest to most specific?

A) Subscription > Management Group > Resource Group > Resource
B) Management Group > Subscription > Resource Group > Resource
C) Resource Group > Subscription > Management Group > Resource
D) Management Group > Resource Group > Subscription > Resource

<details>
<summary>Show Answer</summary>

**Answer: B) Management Group > Subscription > Resource Group > Resource**

Explanation: The hierarchy from broadest to most specific is: Management Groups > Subscriptions > Resource Groups > Resources.
</details>

---

### Question 16
You need to enforce a rule that all resources must have a specific tag. Which feature should you use?

A) RBAC
B) Azure Policy
C) Resource Lock
D) Azure Blueprint

<details>
<summary>Show Answer</summary>

**Answer: B) Azure Policy**

Explanation: Azure Policy enforces organizational standards and can require specific tags on resources.
</details>

---

### Question 17
Which RBAC role allows a user to manage all aspects of resources but NOT assign roles to other users?

A) Owner
B) Contributor
C) Reader
D) User Access Administrator

<details>
<summary>Show Answer</summary>

**Answer: B) Contributor**

Explanation: Contributor has full access to manage resources but cannot assign roles. Only Owner can assign roles.
</details>

---

### Question 18
Which Azure service provides personalized recommendations for security, reliability, performance, and cost?

A) Azure Monitor
B) Azure Advisor
C) Azure Service Health
D) Azure Security Center

<details>
<summary>Show Answer</summary>

**Answer: B) Azure Advisor**

Explanation: Azure Advisor provides personalized best practice recommendations across reliability, security, performance, cost, and operational excellence.
</details>

---

### Question 19
Which tool shows the current health status of Azure services and any planned maintenance?

A) Azure Monitor
B) Azure Advisor
C) Azure Service Health
D) Azure Policy

<details>
<summary>Show Answer</summary>

**Answer: C) Azure Service Health**

Explanation: Azure Service Health provides information about Azure service issues, planned maintenance, and health advisories.
</details>

---

### Question 20
What does Azure DDoS Protection help prevent?

A) Data breaches
B) Malware infections
C) Distributed denial-of-service attacks
D) Unauthorized access

<details>
<summary>Show Answer</summary>

**Answer: C) Distributed denial-of-service attacks**

Explanation: Azure DDoS Protection protects against distributed denial-of-service attacks that attempt to overwhelm resources.
</details>

---

## Section 4: Mixed Topics

### Question 21
Which type of scaling adds more VM instances to handle increased load?

A) Vertical scaling
B) Horizontal scaling
C) Elastic scaling
D) Auto-scaling

<details>
<summary>Show Answer</summary>

**Answer: B) Horizontal scaling**

Explanation: Horizontal scaling (scale out) adds more instances. Vertical scaling (scale up) adds more power to existing instances.
</details>

---

### Question 22
Azure Functions is an example of which computing model?

A) IaaS
B) PaaS
C) SaaS
D) Serverless

<details>
<summary>Show Answer</summary>

**Answer: D) Serverless**

Explanation: Azure Functions is serverless compute - you only pay when your code runs, with no infrastructure management.
</details>

---

### Question 23
Which Azure service stores secrets, keys, and certificates securely?

A) Azure Security Center
B) Azure Key Vault
C) Microsoft Entra ID
D) Azure Information Protection

<details>
<summary>Show Answer</summary>

**Answer: B) Azure Key Vault**

Explanation: Azure Key Vault securely stores and manages secrets, encryption keys, and certificates.
</details>

---

### Question 24
What is the purpose of Azure ARM templates?

A) Monitor resource usage
B) Manage user access
C) Deploy resources consistently using code
D) Backup resources

<details>
<summary>Show Answer</summary>

**Answer: C) Deploy resources consistently using code**

Explanation: ARM (Azure Resource Manager) templates are JSON files that enable Infrastructure as Code for consistent, repeatable deployments.
</details>

---

### Question 25
Which compliance standard is specifically for protecting healthcare data in the United States?

A) GDPR
B) ISO 27001
C) HIPAA
D) SOC 2

<details>
<summary>Show Answer</summary>

**Answer: C) HIPAA**

Explanation: HIPAA (Health Insurance Portability and Accountability Act) is the US standard for protecting healthcare information.
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
- [Microsoft Learn Practice Assessment](https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/practice/assessment)
- [Azure AZ-900 Exam Page](https://learn.microsoft.com/en-us/credentials/certifications/exams/az-900/)
