"""
Generate Mermaid diagrams from deal data to visualize the Buying Process.
Renders to PNG image via mermaid.ink API.
"""
from __future__ import annotations

import base64
import hashlib
import os
import urllib.request
import urllib.parse


CACHE_DIR = os.path.join(os.path.dirname(__file__), "data", "diagram_cache")


def _sanitize(text: str) -> str:
    """Sanitize text for Mermaid labels."""
    if not text:
        return "N/A"
    # Remove characters that break Mermaid syntax
    return (
        text.replace('"', "'")
        .replace("(", "[")
        .replace(")", "]")
        .replace("<", "")
        .replace(">", "")
        .replace("{", "[")
        .replace("}", "]")
        .replace("|", "/")
        .replace("#", "")
        .replace("&", "and")
    )


def _status_color(status: str) -> str:
    """Return a CSS class name based on status."""
    status_lower = (status or "").lower()
    if status_lower == "completed":
        return "completed"
    elif status_lower == "in progress":
        return "inprogress"
    elif status_lower == "bypassed":
        return "bypassed"
    elif status_lower in ("not started", "scheduled"):
        return "notstarted"
    else:
        return "default"


def render_mermaid_to_image(mermaid_code: str) -> bytes | None:
    """Render Mermaid code to a PNG image using mermaid.ink API.
    Returns PNG bytes or None on failure."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)

        # Check cache
        code_hash = hashlib.md5(mermaid_code.encode()).hexdigest()
        cache_path = os.path.join(CACHE_DIR, f"{code_hash}.png")
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()

        # Encode for mermaid.ink
        encoded = base64.urlsafe_b64encode(mermaid_code.encode("utf-8")).decode("ascii")
        url = f"https://mermaid.ink/img/{encoded}?type=png&bgColor=1a1a2e&theme=dark"

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "SalesBrain/1.0")
        with urllib.request.urlopen(req, timeout=15) as resp:
            img_bytes = resp.read()

        # Cache it
        with open(cache_path, "wb") as f:
            f.write(img_bytes)

        return img_bytes
    except Exception as e:
        print(f"Mermaid render error: {e}")
        return None


def generate_mermaid(deal_data: dict) -> str:
    """Generate a Mermaid flowchart from deal data."""
    if not deal_data:
        return ""

    bp = deal_data.get("buying_process", {})
    steps = bp.get("buying_steps", [])

    if not steps:
        return ""

    lines = ["graph TD"]

    # Style definitions
    lines.append("    classDef completed fill:#10b981,stroke:#059669,color:#fff,stroke-width:2px")
    lines.append("    classDef inprogress fill:#3b82f6,stroke:#2563eb,color:#fff,stroke-width:2px")
    lines.append("    classDef notstarted fill:#6b7280,stroke:#4b5563,color:#fff,stroke-width:2px")
    lines.append("    classDef bypassed fill:#f59e0b,stroke:#d97706,color:#fff,stroke-width:2px")
    lines.append("    classDef default fill:#8b5cf6,stroke:#7c3aed,color:#fff,stroke-width:2px")
    lines.append("")

    # Build nodes and edges
    step_ids = {}
    for i, step in enumerate(steps):
        step_name = step.get("name", f"Step {i+1}")
        step_id = f"step{i}"
        step_ids[step_name] = step_id

        status = step.get("status", "Not Started")
        timeline = step.get("timeline", "")
        product = ", ".join(step.get("product", [])) if step.get("product") else ""
        buyer = step.get("buyer_owner", "")

        # Build simple label (no HTML, use newlines)
        label_parts = [_sanitize(step_name)]
        label_parts.append(f"Status: {_sanitize(status)}")
        if timeline:
            label_parts.append(f"Timeline: {_sanitize(timeline)}")
        if product:
            label_parts.append(f"Product: {_sanitize(product)}")
        if buyer:
            label_parts.append(f"Buyer: {_sanitize(buyer)}")

        # Add actors summary
        actors = step.get("actors", {})
        sigs = actors.get("signatories", [])
        evals_list = actors.get("evaluators", [])
        infs = actors.get("influencers", [])

        if sigs:
            sig_names = [_sanitize(s.get("name", "?")) for s in sigs]
            label_parts.append(f"Signatory: {', '.join(sig_names)}")
        if evals_list:
            eval_names = [_sanitize(e.get("name", "?")) for e in evals_list]
            label_parts.append(f"Evaluator: {', '.join(eval_names)}")
        if infs:
            inf_names = [_sanitize(inf.get("name", "?")) for inf in infs]
            label_parts.append(f"Influencer: {', '.join(inf_names)}")

        label = "\\n".join(label_parts)
        css_class = _status_color(status)

        lines.append(f'    {step_id}["{label}"]')
        lines.append(f"    class {step_id} {css_class}")
        lines.append("")

    # Add dependency edges
    for i, step in enumerate(steps):
        step_name = step.get("name", f"Step {i+1}")
        step_id = step_ids.get(step_name, f"step{i}")
        deps = step.get("step_dependency", [])
        if deps:
            for dep_name in deps:
                dep_id = step_ids.get(dep_name)
                if dep_id:
                    lines.append(f"    {dep_id} --> {step_id}")

    # If no dependencies, show sequential flow
    has_deps = any(step.get("step_dependency") for step in steps)
    if not has_deps and len(steps) > 1:
        for i in range(len(steps) - 1):
            lines.append(f"    step{i} --> step{i+1}")

    return "\n".join(lines)


def generate_actors_table(deal_data: dict) -> list[dict]:
    """Generate a flat table of all actors across all steps for display."""
    rows = []
    bp = deal_data.get("buying_process", {})
    steps = bp.get("buying_steps", [])

    for step in steps:
        step_name = step.get("name", "Unknown")
        actors = step.get("actors", {})

        for sig in actors.get("signatories", []):
            rows.append({
                "Step": step_name,
                "Role": "🔑 Signatory",
                "Name": sig.get("name", "N/A"),
                "Title": sig.get("title", ""),
                "Sign-off": sig.get("sign_off_status", "Pending"),
                "Status": sig.get("status", "N/A"),
                "Timeline": sig.get("timeline", ""),
                "Criteria": len(sig.get("criteria", [])),
            })

        for ev in actors.get("evaluators", []):
            rows.append({
                "Step": step_name,
                "Role": "🔍 Evaluator",
                "Name": ev.get("name", "N/A"),
                "Title": ev.get("title", ""),
                "Sign-off": "—",
                "Status": ev.get("status", "N/A"),
                "Timeline": ev.get("timeline", ""),
                "Criteria": len(ev.get("criteria", [])),
            })

        for inf in actors.get("influencers", []):
            rows.append({
                "Step": step_name,
                "Role": "💬 Influencer",
                "Name": inf.get("name", "N/A"),
                "Title": inf.get("title", ""),
                "Sign-off": "—",
                "Status": inf.get("status", "N/A"),
                "Timeline": inf.get("timeline", ""),
                "Criteria": len(inf.get("criteria", [])),
            })

    return rows
