# RevCortex — Buying Process Mastery Design

> Source: `RevCortex Design_Detailed_Buying Process_Copy.pptx`

---

## 1. First Principles — What is a Deal?

A deal is:
**Stakeholders → evaluating alternatives → against requirements → through their buying process → signing off on their criteria → within a timeline → to purchase products → at agreed price and terms → governed by mutual execution commitments → that can be implemented → and adopted → to realize quantified value**

Simplified: **A deal is a Signatory signing off on Criteria in a Buying Process within a Timeline.**

---

## 2. Forecast Readiness Dimensions (10)

A deal must fulfill **all 10 dimensions** to be forecast-ready:

| # | Dimension |
|---|-----------|
| 1 | Budget Closure |
| 2 | Function Usage Closure |
| 3 | Technical Closure |
| 4 | Security & Compliance Closure |
| 5 | Business Case Closure |
| 6 | Commercial Closure |
| 7 | Contract Closure |
| 8 | Implementation Readiness Closure |
| 9 | Adoption Readiness Closure |
| 10 | Operational Closure |

---

## 3. Core Entities (7)

| Entity | Example |
|--------|---------|
| **Buying Step** | Security Review |
| **Actor** | John Smith — CFO — Finance |
| **Product** | Analytics Platform |
| **Validation Criterion** | "SOC2 compliance required" |
| **Timeline** | "Before end of Q3" |
| **Evidence Artifact** | Security approval email |
| **Engagement Event** | Security review call on Oct 10 |

---

## 4. Entity Relationships (15)

| # | Relationship | Ontology | Example |
|---|-------------|----------|---------|
| 1 | Step → Actor | `involves` | Security Review involves John Smith (CFO) |
| 2 | Actor → Step (Role) | `plays_role_in` | John Smith plays_role_in Security Review as Signatory |
| 3 | Step → Criterion | `requires` | Security Review requires "SOC2 compliance required" |
| 4 | Criterion → Actor | `owned_by` | "SOC2 compliance required" owned_by Head of Security |
| 5 | Step → Step (Dependency) | `depends_on` | Legal Review depends_on Security Review |
| 6 | Step → Product | `applies_to` | Security Review applies_to Analytics Platform |
| 7 | Criterion → Product | `applies_to` | "SOC2 compliance" applies_to Analytics Platform |
| 8 | Step → Timeline | `constrained_by` | Security Review constrained_by end of Q3 |
| 9 | Criterion → Timeline | `has_deadline` | "Security questionnaire complete" has_deadline Oct 20 |
| 10 | Step → Evidence | `evidenced_by` | Security Review evidenced_by approval email |
| 11 | Criterion → Evidence | `proven_by` | "SOC2 compliance" proven_by audit report |
| 12 | Criterion → Criterion (Dep) | `depends_on` | "Security approval" depends_on "Pen test complete" |
| 13 | Criterion → Criterion (Inherit) | `inherited_from` | CFO "Budget approved" inherited_from Finance "Budget analysis" |
| 14 | Actor → Actor (Org) | `reports_to` | Head of Security reports_to CIO |
| 15 | Actor → Engagement Event | `participated_in` | CFO participated_in Oct 10 call |

---

## 5. Deal & Buying Process

- A deal has **≥ 1 product**
- CRM lifecycle: Lead → Opportunity → Closure
- **RevCortex starts at the Opportunity stage**
- **1 Deal : 1 Buying Process**
- Multi-product deals: branching within 1 Buying Process

### Rule — Deal Outcome
A deal = **closed-won** only if **all required buying steps** in the buying process are **complete + have evidence**.

---

## 6. Buying Step — Attributes & Rules

### Attributes

| # | Attribute | Details |
|---|-----------|---------|
| 1 | **Name** | e.g. Discovery, Demo, PoC, Pilot |
| 2 | **Status** | Not Started / In Progress / Completed / Bypassed |
| 3 | **Evidence** | Latest artifacts backing status (from calls/emails), with Last Updated timestamp |
| 4 | **Timeline** | Date by which the step must close |
| 5 | **Product** | Tagged product(s) if >1 in deal |
| 6 | **Forecast Readiness Dimension** | One of the 10 dimensions |
| 7 | **Step Dependency** | Zero or more prerequisite Buying Steps |
| 8 | **Buyer Owner** | Who owns step execution from buyer org |
| 9 | **Seller Owner** | Who owns step execution from seller org |
| 10 | **Actors** | One of: Signatory, Evaluator, Influencer |

### Rules
- A buying process contains **≥ 1 Buying Step**
- System prevents **circular dependencies** in Step Dependency graph
- A buying step must have **all defined attributes**
- A buying step applies to **≥ 1 product** in the deal
- **Sequential**: dependent steps complete only after prerequisites complete
- **Parallel**: independent steps execute simultaneously
- Every buying step requires **≥ 1 Signatory** actor
- If **≥ 1 required Actor differs** for 2 products → create a **separate Buying Step**
- Step dependency **blocks completion, not start** (steps can execute in parallel; dependent step completes only after prerequisite completes)
- Step completion requires: **all Actors' criteria satisfied + evidenced**

---

## 7. Actor — Roles & Rules

An Actor is a stakeholder assigned a role in influencing, evaluating, or approving a Buying Step.

### Three Roles

| Role | Criteria Mandatory? | Sign-off Authority? | Can Block Step? |
|------|---------------------|---------------------|-----------------|
| **Signatory (S)** | Yes | ✅ Yes | ✅ Yes |
| **Evaluator (E)** | Yes | ❌ No | ✅ Yes (blocks until criteria satisfied/bypassed) |
| **Influencer (I)** | No (non-mandatory) | ❌ No | ❌ No |

### Signatory Details
- Has sign-off authority (mandatory)
- May or may not evaluate directly
- Must have a valid evaluation basis, satisfied by:
  - The Signatory's own Evaluation Criteria, **OR**
  - Inherited Evaluation Criteria from Evaluators or another Signatory
- Final approver of the Buying Step

### Rules
- **≥ 1 Signatory** per step
- Signatory: **≥ 1 mandatory Evaluation Criterion**
- Evaluator: **≥ 1 mandatory Criterion**
- Influencer: **≥ 1 non-mandatory Criterion**
- Step complete only if **all mandatory criteria completed/bypassed AND signed off/bypassed**

### Differentiators
- **Influencer vs Evaluator**: Criteria mandatory for Evaluator, non-mandatory for Influencer
- **Evaluator vs Signatory**: Signatory has go/no-go sign-off on top of evaluation criteria

---

## 8. Criterion — Attributes & Rules

A Criterion is a specific condition that must be met (or influenced) by an Actor to complete their role in a Buying Step.

### Attributes

| # | Attribute | Details |
|---|-----------|---------|
| 1 | **Product** | Which product(s) this criterion applies to |
| 2 | **Description** | What must be true/satisfied (verifiable format) |
| 3 | **Type** | Mandatory (blocks step) / Non-Mandatory (informational) |
| 4 | **Timeline** | Target completion date (must be ≤ Actor Timeline) |
| 5 | **Dependency** | Prerequisites — can depend on other criteria (within/across actors/steps) or on an actor (inherits ALL that actor's criteria) |
| 6 | **Status** | Not Started / In Progress / Completed / Bypassed |

### Timeline Rollup
`Criterion → Actor → Step`

### Rules
- All Signatory and Evaluator criteria are **mandatory for closure** (completed or bypassed)
- Criterion can depend on **one or more other criteria** (within or across actor/step boundaries)
- Criterion can depend on **any actor** → inherits all that actor's criteria
- If only one stakeholder → they are Signatory with **≥ 1 criterion**
- Signatory may delegate evaluation → their criteria must **explicitly depend on Evaluators or another Signatory**
- System prevents **circular dependencies** in Criterion Dependency graph
  - No criterion can transitively depend on itself
  - Applies to direct criterion dependencies AND actor-inherited dependencies
  - System blocks saving invalid dependency configs

---

## 9. Data Structure (Final Hierarchy)

```
Deal
└── Buying Process (1:1 with Deal)
    └── Buying Step (1 to N)
        ├── Name
        ├── Status (Not Started | In Progress | Completed | Bypassed)
        ├── Evidence (artifacts + timestamp)
        ├── Timeline
        ├── Product (≥1)
        ├── Forecast Readiness Dimension (1 of 10)
        ├── Step Dependency (0 to N prerequisite steps)
        ├── Buyer Owner
        ├── Seller Owner
        └── Actors (1 to N)
            ├── Signatory (≥1 per step)
            │   ├── Name / Title / Dept
            │   ├── Timeline
            │   ├── Status
            │   ├── Sign Off Status
            │   └── Evaluation Criteria (≥1, mandatory)
            │       ├── Product
            │       ├── Description
            │       ├── Type (Mandatory)
            │       ├── Timeline
            │       ├── Dependency
            │       ├── Status
            │       ├── Evidence
            │       └── (may inherit from Evaluators)
            ├── Evaluator (0 to N)
            │   ├── Name / Title / Dept
            │   ├── Timeline
            │   ├── Status
            │   └── Evaluation Criteria (≥1, mandatory)
            │       ├── Product
            │       ├── Description
            │       ├── Type (Mandatory)
            │       ├── Timeline
            │       ├── Dependency
            │       ├── Status
            │       └── Evidence
            └── Influencer (0 to N)
                ├── Name / Title / Dept
                ├── Timeline
                ├── Status
                └── Influencing Criteria (≥1, non-mandatory)
                    ├── Product
                    ├── Description
                    ├── Type (Non-Mandatory)
                    ├── Timeline
                    ├── Dependency
                    └── Status
```

---

## 10. Graph Model (DAG)

The Buying Process is modeled as a **Directed Acyclic Graph (DAG)**:
- **Nodes**: Buying Steps, Actors, Criteria, Products, Timelines, Evidence Artifacts, Engagement Events
- **Edges**: The 15 relationships listed above
- **Constraints**: No circular dependencies in Step or Criterion dependency graphs
