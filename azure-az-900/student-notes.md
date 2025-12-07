# Azure AZ-900: Azure Fundamentals - Student Notes

## Course Overview

This 3-day certification prep course covers all domains tested on the Microsoft Azure Fundamentals (AZ-900) exam.

**Exam Details:**
- Cost: $165 USD
- Questions: 40-60
- Passing Score: 700/1000
- Duration: ~60 minutes
- No prerequisites required

---

## Day 1: Cloud Concepts (25-30%)

### What is Cloud Computing?

Cloud computing is the delivery of computing services over the internet:
- Servers and compute power
- Storage and databases
- Networking
- Software and analytics
- AI and machine learning

**Pay-as-you-go pricing:** Only pay for what you use.

### Benefits of Cloud Computing

| Benefit | Description |
|---------|-------------|
| **High Availability** | Systems remain operational. SLAs guarantee uptime |
| **Scalability** | Vertical (more power) or Horizontal (more instances) |
| **Elasticity** | Auto-scale based on demand |
| **Global Reach** | Deploy worldwide, reduce latency |
| **Disaster Recovery** | Backup and replicate across regions |
| **Agility** | Deploy and experiment quickly |

### Cloud Service Types

| Type | You Manage | Provider Manages | Examples |
|------|-----------|------------------|----------|
| **IaaS** | OS, Apps, Data | Hardware, Network | Azure VMs |
| **PaaS** | Apps, Data | OS, Runtime, Hardware | App Service |
| **SaaS** | Data only | Everything else | Microsoft 365 |

**Remember:** IaaS = most control, SaaS = least management

### Shared Responsibility Model

**Customer ALWAYS responsible for:**
- Data classification and accountability
- Account and identity management
- Device security (endpoints)

**Provider ALWAYS responsible for:**
- Physical data centers
- Physical network
- Physical hosts

### Cloud Deployment Models

| Model | Description | Use Case |
|-------|-------------|----------|
| **Public** | Shared, provider-owned | General workloads |
| **Private** | Dedicated, organization-owned | Sensitive data |
| **Hybrid** | Combination of both | Most flexibility |

### CapEx vs OpEx

| CapEx | OpEx |
|-------|------|
| Upfront infrastructure investment | Ongoing service spending |
| Buy servers | Pay for usage |
| Fixed costs | Variable costs |
| Traditional IT | Cloud model |

**Cloud = Shift from CapEx to OpEx**

### Azure Global Infrastructure

**Hierarchy:**
1. **Geography** - Americas, Europe, Asia Pacific
2. **Region Pair** - Two regions for disaster recovery
3. **Region** - Geographic area with data centers
4. **Availability Zone** - Separate physical locations within region

**Key Points:**
- 60+ regions worldwide
- Minimum 3 availability zones per enabled region
- 99.99% VM SLA with availability zones

---

## Day 2: Core Azure Services (35-40%)

### Compute Services

| Service | Type | Description |
|---------|------|-------------|
| **Virtual Machines** | IaaS | Full control over OS |
| **VM Scale Sets** | IaaS | Auto-scaling VM groups |
| **App Service** | PaaS | Web app hosting |
| **Azure Functions** | Serverless | Event-driven code |
| **Container Instances** | PaaS | Run containers |
| **Azure Kubernetes Service** | PaaS | Managed Kubernetes |
| **Azure Virtual Desktop** | PaaS | Desktop virtualization |

### Networking Services

| Service | Purpose |
|---------|---------|
| **Virtual Network (VNet)** | Private network in Azure |
| **VPN Gateway** | Connect on-prem via encrypted tunnel |
| **ExpressRoute** | Private connection (not over internet) |
| **Azure Load Balancer** | Distribute traffic across VMs |
| **Azure DNS** | Host DNS domains |
| **Network Security Groups** | Filter network traffic |

**VPN vs ExpressRoute:**
- VPN: Over internet, encrypted
- ExpressRoute: Private, higher bandwidth, more reliable

### Storage Services

| Service | Use Case |
|---------|----------|
| **Blob Storage** | Unstructured data (images, videos) |
| **File Storage** | SMB file shares |
| **Queue Storage** | Messaging between apps |
| **Table Storage** | NoSQL key-value |

**Storage Tiers:**
- Hot: Frequently accessed
- Cool: Infrequent access (30+ days)
- Archive: Rarely accessed (180+ days)

**Redundancy Options:**
- LRS: 3 copies, single datacenter
- ZRS: 3 zones in region
- GRS: 6 copies, 2 regions
- GZRS: ZRS + GRS combined

### Database Services

| Service | Type | Use Case |
|---------|------|----------|
| **Azure SQL Database** | Relational | Managed SQL Server |
| **Cosmos DB** | NoSQL | Global, multi-model |
| **Azure Database for MySQL** | Relational | Open-source MySQL |
| **Azure Database for PostgreSQL** | Relational | Open-source PostgreSQL |

### Identity Services

**Microsoft Entra ID (formerly Azure AD):**
- Cloud identity service
- Single Sign-On (SSO)
- Multi-Factor Authentication (MFA)
- Conditional Access policies

**Entra ID vs AD DS:**
- Entra ID: Cloud-based
- AD DS: On-premises directory

### Management Tools

| Tool | Description |
|------|-------------|
| **Azure Portal** | Web-based GUI |
| **Azure CLI** | Command-line (cross-platform) |
| **PowerShell** | Scripting with Az module |
| **Cloud Shell** | Browser-based shell |
| **Mobile App** | iOS/Android management |
| **ARM Templates** | Infrastructure as Code (JSON) |

---

## Day 3: Management & Governance (30-35%)

### Cost Management

**Factors Affecting Cost:**
- Resource type
- Usage (pay for what you use)
- Region
- Tier (Premium vs Standard)
- Bandwidth (egress costs money)

**Cost Tools:**

| Tool | Purpose |
|------|---------|
| **Pricing Calculator** | Estimate costs before deploying |
| **TCO Calculator** | Compare on-prem vs cloud |
| **Cost Management** | Monitor and analyze spending |
| **Budgets** | Set limits with alerts |
| **Advisor** | Cost recommendations |

**Cost Saving Options:**
- Reserved Instances: 1-3 year commitment = up to 72% savings
- Spot VMs: Use unused capacity at discount
- Hybrid Benefit: Use existing Windows/SQL licenses

### Governance

**Management Hierarchy:**
```
Management Groups
    └── Subscriptions
            └── Resource Groups
                    └── Resources
```

**Governance Features:**

| Feature | Purpose |
|---------|---------|
| **Azure Policy** | Enforce standards and compliance |
| **RBAC** | Role-based access control |
| **Resource Locks** | Prevent accidental changes |
| **Tags** | Organize and track resources |
| **Blueprints** | Repeatable environment setup |

### RBAC (Role-Based Access Control)

**Components:**
- Security Principal: Who (user, group, service principal)
- Role Definition: What they can do
- Scope: Where it applies

**Built-in Roles:**

| Role | Permissions |
|------|------------|
| Owner | Full access + assign roles |
| Contributor | Full access, can't assign roles |
| Reader | View only |
| User Access Admin | Manage access only |

### Azure Policy

**Purpose:** Enforce organizational standards

**Policy vs RBAC:**
- Policy = What resources can do
- RBAC = What users can do

**Common Policies:**
- Require tags
- Restrict VM sizes
- Enforce allowed regions
- Require encryption

### Resource Locks

| Lock Type | Effect |
|-----------|--------|
| CanNotDelete | Read/modify OK, no delete |
| ReadOnly | Read only, no changes |

**Important:** Locks apply to ALL users, even Owners!

### Tags

Key-value pairs for organizing resources:
- Cost tracking: `Department: Marketing`
- Environment: `Env: Production`
- Owner: `Owner: John.Doe`

**Note:** Tags are NOT inherited by default.

### Compliance

**Trust Center:** Security, privacy, compliance info

**Key Standards:**
- GDPR: EU data protection
- ISO 27001: Security management
- SOC 1/2/3: Service controls
- HIPAA: Healthcare (US)
- FedRAMP: US government

**Tools:**
- Compliance Manager
- Service Trust Portal
- Microsoft Purview

### Monitoring

| Service | Purpose |
|---------|---------|
| **Azure Monitor** | Metrics, logs, alerts |
| **Service Health** | Azure platform status |
| **Azure Advisor** | Best practice recommendations |

### Security

**Defense in Depth Layers:**
1. Physical Security
2. Identity & Access
3. Perimeter
4. Network
5. Compute
6. Application
7. Data

**Security Services:**

| Service | Purpose |
|---------|---------|
| **Defender for Cloud** | Security posture, threats |
| **Azure Firewall** | Managed network firewall |
| **Key Vault** | Secrets, keys, certificates |
| **DDoS Protection** | Attack mitigation |
| **NSGs** | Network traffic filtering |

---

## Key Terms Quick Reference

| Term | Definition |
|------|------------|
| Region | Geographic area with data centers |
| Availability Zone | Separate physical location in region |
| Subscription | Billing and access boundary |
| Resource Group | Container for related resources |
| ARM | Azure Resource Manager |
| SLA | Service Level Agreement |
| HA | High Availability |
| DR | Disaster Recovery |
| NSG | Network Security Group |
| VNet | Virtual Network |
| RBAC | Role-Based Access Control |
| MFA | Multi-Factor Authentication |
| SSO | Single Sign-On |

---

## Exam Tips

1. **Know cloud concepts:**
   - IaaS vs PaaS vs SaaS
   - Public vs Private vs Hybrid
   - CapEx vs OpEx

2. **Understand Azure hierarchy:**
   - Management Groups > Subscriptions > Resource Groups > Resources

3. **Know when to use each service:**
   - VMs for IaaS control
   - App Service for web apps
   - Functions for serverless
   - Cosmos DB for global NoSQL

4. **Remember governance tools:**
   - Policy for resource rules
   - RBAC for user access
   - Locks for protection

5. **Practice in Azure portal**

---

## Additional Resources

- [Microsoft Learn AZ-900 Path](https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/)
- [AZ-900 Study Guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/az-900)
- [Practice Assessment](https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/practice/assessment)
- [Azure Free Account](https://azure.microsoft.com/free/)
