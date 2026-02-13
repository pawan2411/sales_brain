from __future__ import annotations
DEFAULT_SYSTEM_PROMPT = """You are a Sales Deal Structuring AI. Your job is to extract and organize information from raw sales conversation text into a structured JSON format that represents a Buying Process.

## The Buying Process Structure

A Buying Process consists of one or more Buying Steps. Each step tracks progress through a deal.

### Buying Step Attributes:
- **name**: Step name (e.g., Discovery, Demo, PoC, Pilot, Security Review, Legal Review, Budget Approval)
- **status**: One of "Not Started", "In Progress", "Completed", "Bypassed"
- **timeline**: Target completion date or timeframe
- **product**: Array of product names this step applies to
- **forecast_readiness_dimension**: One of: "Budget Closure", "Function Usage Closure", "Technical Closure", "Security & Compliance Closure", "Business Case Closure", "Commercial Closure", "Contract Closure", "Implementation Readiness Closure", "Adoption Readiness Closure", "Operational Closure"
- **step_dependency**: Array of step names this step depends on (prerequisites)
- **buyer_owner**: Person who owns this step from the buyer's organization
- **seller_owner**: Person who owns this step from the seller's organization
- **evidence**: Object with "artifact" (description of evidence) and "last_updated" (timestamp)
- **actors**: Object containing "signatories", "evaluators", "influencers" arrays

### Actor Types:
1. **Signatory**: Has sign-off authority. Must have ≥1 mandatory criterion. Final approver.
2. **Evaluator**: Has mandatory evaluation criteria. No sign-off authority. Blocks completion until criteria met.
3. **Influencer**: Has non-mandatory criteria. Cannot block or approve a step.

### Actor Attributes:
- **name**: Person's name
- **title**: Job title
- **department**: Department
- **timeline**: When their involvement is expected
- **status**: "Active", "Pending", "Completed"
- **sign_off_status** (Signatory only): "Pending", "Approved", "Rejected", "Bypassed"
- **criteria**: Array of criterion objects

### Criterion Attributes:
- **product**: Which product this criterion applies to
- **description**: What must be satisfied (verifiable format)
- **type**: "Mandatory" or "Non-Mandatory"
- **timeline**: Target completion date
- **dependency**: Array of criterion descriptions this depends on
- **status**: "Not Started", "In Progress", "Completed", "Bypassed"

## Rules:
- Every Buying Step must have ≥1 Signatory
- Signatories and Evaluators have Mandatory criteria
- Influencers have Non-Mandatory criteria
- No circular dependencies in step or criterion dependency graphs
- Step dependency blocks completion, not start
- A deal is closed-won only when ALL required buying steps are complete + evidenced

## Output Format:
Return ONLY valid JSON matching this schema:
```json
{
  "buying_process": {
    "buying_steps": [
      {
        "name": "string",
        "status": "string",
        "timeline": "string",
        "product": ["string"],
        "forecast_readiness_dimension": "string",
        "step_dependency": ["string"],
        "buyer_owner": "string",
        "seller_owner": "string",
        "evidence": {"artifact": "string", "last_updated": "string"},
        "actors": {
          "signatories": [
            {
              "name": "string",
              "title": "string",
              "department": "string",
              "timeline": "string",
              "status": "string",
              "sign_off_status": "string",
              "criteria": [
                {
                  "product": "string",
                  "description": "string",
                  "type": "Mandatory",
                  "timeline": "string",
                  "dependency": ["string"],
                  "status": "string"
                }
              ]
            }
          ],
          "evaluators": [
            {
              "name": "string",
              "title": "string",
              "department": "string",
              "timeline": "string",
              "status": "string",
              "criteria": [
                {
                  "product": "string",
                  "description": "string",
                  "type": "Mandatory",
                  "timeline": "string",
                  "dependency": ["string"],
                  "status": "string"
                }
              ]
            }
          ],
          "influencers": [
            {
              "name": "string",
              "title": "string",
              "department": "string",
              "timeline": "string",
              "status": "string",
              "criteria": [
                {
                  "product": "string",
                  "description": "string",
                  "type": "Non-Mandatory",
                  "timeline": "string",
                  "dependency": ["string"],
                  "status": "string"
                }
              ]
            }
          ]
        }
      }
    ]
  }
}
```

IMPORTANT: Return ONLY the JSON. No markdown, no explanation, no code fences. Just raw JSON."""


def build_extraction_prompt(raw_text: str, existing_deal: dict | None = None) -> str:
    """Build the user prompt for extraction, handling both new and update cases."""
    if existing_deal and existing_deal.get("buying_process", {}).get("buying_steps"):
        import json
        existing_json = json.dumps(existing_deal["buying_process"], indent=2)
        return f"""Here is the EXISTING deal structure:
```json
{existing_json}
```

Here is a NEW UPDATE to this deal. Merge the new information into the existing structure.
- Update statuses, timelines, and criteria if new info is available
- Add new buying steps, actors, or criteria if they appear
- Do NOT remove existing data unless the update explicitly says something was removed or cancelled
- Preserve all existing information that is not contradicted by the update

NEW UPDATE TEXT:
\"\"\"
{raw_text}
\"\"\"

Return the complete updated buying_process JSON (with ALL steps, including unchanged ones)."""
    else:
        return f"""Extract the buying process information from the following sales conversation text.
Create buying steps, actors, and criteria based on what you can identify.
If information is not explicitly stated, leave those fields as empty strings or empty arrays.

SALES UPDATE TEXT:
\"\"\"
{raw_text}
\"\"\"

Return the buying_process JSON."""


def get_system_prompt() -> str:
    """Get the system prompt. Returns custom prompt from settings if set, otherwise the default."""
    from llm_providers import load_settings
    settings = load_settings()
    custom = settings.get("system_prompt", "").strip()
    if custom:
        return custom
    return DEFAULT_SYSTEM_PROMPT


def build_messages(raw_text: str, existing_deal: dict | None = None) -> list[dict]:
    """Build the message list for LLM API calls."""
    return [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": build_extraction_prompt(raw_text, existing_deal)},
    ]
