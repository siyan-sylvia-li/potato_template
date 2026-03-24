"""
Convert final_data_with_gliner.json to POTATO-compatible JSONL format.

POTATO config (pupa_v2_prolific.yaml) expects each item to have:
  - id          (id_key)
  - user_query  (text_key)
  - context     (context_key)
"""

import json
import os

INPUT_FILE = "data/final_data_with_gliner.json"
OUTPUT_FILE = "data/potato_data.jsonl"


def format_pii_info(item: dict) -> str:
    """Build an HTML context block from PII and response fields."""
    parts = []

    # Conversation history (if present)
    # history = item.get("conversation_history", "None")
    # if history and history.strip().lower() != "none":
    #     parts.append(
    #         "<div class='context-block'>"
    #         "<strong>Conversation History:</strong>"
    #         f"<pre>{history}</pre>"
    #         "</div>"
    #     )

    # AI response
    # target = item.get("target_response", "")
    # if target:
    #     parts.append(
    #         "<div class='context-block'>"
    #         "<strong>AI Response:</strong>"
    #         f"<pre>{target}</pre>"
    #         "</div>"
    #     )

    # PII detected by GLiNER
    pii_gliner = item.get("pii_gliner", "")
    pii_types = item.get("pii_gliner_types", [])
    if pii_gliner:
        entities = pii_gliner.split("||")
        pairs = zip(entities, pii_types) if pii_types else ((e, "unknown") for e in entities)
        rows = "".join(
            f"<tr><td>{e.strip()}</td><td>{t}</td></tr>"
            for e, t in pairs
        )
        parts.append(
            "<div class='context-block'>"
            "<strong>PII detected by GLiNER:</strong>"
            "<table border='1' style='border-collapse:collapse;margin-top:4px'>"
            "<thead><tr><th>Entity</th><th>Type</th></tr></thead>"
            f"<tbody>{rows}</tbody>"
            "</table>"
            "</div>"
        )

    # # Category
    # category = item.get("categorys_analysis", "")
    # if category:
    #     parts.append(
    #         "<div class='context-block'>"
    #         f"<strong>Category:</strong> {category}"
    #         "</div>"
    #     )

    # # Redacted query
    # redacted = item.get("redacted_query", "")
    # if redacted:
    #     parts.append(
    #         "<div class='context-block'>"
    #         "<strong>Redacted Query:</strong>"
    #         f"<pre>{redacted}</pre>"
    #         "</div>"
    #     )

    return "\n".join(parts)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for idx, item in enumerate(data):
            potato_item = {
                "id": idx,
                "user_query": item["user_query"],
                "context": "N/A",
                # Preserve remaining fields so POTATO can pass them through
                "pii_units": item.get("pii_units", ""),
                "pii_gliner": item.get("pii_gliner", ""),
                "pii_gliner_types": item.get("pii_gliner_types", []),
                "categorys_analysis": item.get("categorys_analysis", ""),
            }
            out.write(json.dumps(potato_item, ensure_ascii=False) + "\n")

    print(f"Wrote {len(data)} items to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
