import json
import os
from datetime import datetime

DEALS_DIR = os.path.join(os.path.dirname(__file__), "data", "deals")

EMPTY_DEAL = {
    "deal_name": "",
    "created_at": "",
    "updated_at": "",
    "buying_process": {
        "buying_steps": []
    },
    "update_history": []
}

EMPTY_BUYING_STEP = {
    "name": "",
    "status": "Not Started",
    "timeline": "",
    "product": [],
    "forecast_readiness_dimension": "",
    "step_dependency": [],
    "buyer_owner": "",
    "seller_owner": "",
    "evidence": {
        "artifact": "",
        "last_updated": ""
    },
    "actors": {
        "signatories": [],
        "evaluators": [],
        "influencers": []
    }
}


def list_deals() -> list[str]:
    """List all deal names from the deals directory."""
    os.makedirs(DEALS_DIR, exist_ok=True)
    deals = []
    for fname in sorted(os.listdir(DEALS_DIR)):
        if fname.endswith(".json"):
            deals.append(fname.replace(".json", ""))
    return deals


def load_deal(deal_name: str) -> dict | None:
    """Load a deal by name. Returns None if not found."""
    filepath = os.path.join(DEALS_DIR, f"{deal_name}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)


def save_deal(deal_name: str, deal_data: dict):
    """Save deal data to a JSON file."""
    os.makedirs(DEALS_DIR, exist_ok=True)
    deal_data["updated_at"] = datetime.now().isoformat()
    filepath = os.path.join(DEALS_DIR, f"{deal_name}.json")
    with open(filepath, "w") as f:
        json.dump(deal_data, f, indent=2)


def create_deal(deal_name: str) -> dict:
    """Create a new empty deal. Returns the deal data."""
    deal = EMPTY_DEAL.copy()
    deal["deal_name"] = deal_name
    deal["created_at"] = datetime.now().isoformat()
    deal["updated_at"] = deal["created_at"]
    deal["buying_process"] = {"buying_steps": []}
    deal["update_history"] = []
    save_deal(deal_name, deal)
    return deal


def add_update_to_history(deal_data: dict, raw_text: str, extracted_json: dict) -> dict:
    """Add an update entry to the deal's history."""
    deal_data["update_history"].append({
        "timestamp": datetime.now().isoformat(),
        "raw_text": raw_text,
        "extracted_data": extracted_json
    })
    return deal_data


def deal_to_text_summary(deal_data: dict) -> str:
    """Convert deal data to a readable text summary."""
    if not deal_data:
        return "No deal data."

    lines = [f"# Deal: {deal_data.get('deal_name', 'Unknown')}"]
    lines.append(f"Created: {deal_data.get('created_at', 'N/A')}")
    lines.append(f"Last Updated: {deal_data.get('updated_at', 'N/A')}")
    lines.append("")

    bp = deal_data.get("buying_process", {})
    steps = bp.get("buying_steps", [])

    if not steps:
        lines.append("No buying steps recorded yet.")
        return "\n".join(lines)

    for i, step in enumerate(steps, 1):
        lines.append(f"## Buying Step {i}: {step.get('name', 'Unnamed')}")
        lines.append(f"- Status: {step.get('status', 'N/A')}")
        lines.append(f"- Timeline: {step.get('timeline', 'N/A')}")
        lines.append(f"- Product: {', '.join(step.get('product', [])) if step.get('product') else 'N/A'}")
        lines.append(f"- Forecast Readiness: {step.get('forecast_readiness_dimension', 'N/A')}")
        lines.append(f"- Dependencies: {', '.join(step.get('step_dependency', [])) if step.get('step_dependency') else 'None'}")
        lines.append(f"- Buyer Owner: {step.get('buyer_owner', 'N/A')}")
        lines.append(f"- Seller Owner: {step.get('seller_owner', 'N/A')}")

        actors = step.get("actors", {})
        for sig in actors.get("signatories", []):
            lines.append(f"  - **Signatory**: {sig.get('name', 'N/A')} | Timeline: {sig.get('timeline', 'N/A')} | Sign-off: {sig.get('sign_off_status', 'Pending')}")
            for crit in sig.get("criteria", []):
                lines.append(f"    - Criterion: {crit.get('description', 'N/A')} [{crit.get('status', 'N/A')}]")

        for ev in actors.get("evaluators", []):
            lines.append(f"  - **Evaluator**: {ev.get('name', 'N/A')} | Timeline: {ev.get('timeline', 'N/A')}")
            for crit in ev.get("criteria", []):
                lines.append(f"    - Criterion: {crit.get('description', 'N/A')} [{crit.get('status', 'N/A')}]")

        for inf in actors.get("influencers", []):
            lines.append(f"  - **Influencer**: {inf.get('name', 'N/A')} | Timeline: {inf.get('timeline', 'N/A')}")
            for crit in inf.get("criteria", []):
                lines.append(f"    - Criterion: {crit.get('description', 'N/A')} [{crit.get('status', 'N/A')}]")

        lines.append("")

    return "\n".join(lines)
