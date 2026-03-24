"""
Collate POTATO annotation results from all annotator user_state.json files
into a single CSV with one row per (annotator, instance).

Output columns:
  annotator_id, instance_id, label, user_query, pii_units, pii_gliner,
  pii_gliner_types, categorys_analysis
"""

import json
import csv
import os
import glob
import argparse


def load_data_index(jsonl_path):
    """Return a dict mapping instance id (str) -> data row (dict)."""
    index = {}
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            index[str(row["id"])] = row
    return index


def extract_label(label_entries):
    """
    instance_id_to_label_to_value entries look like:
      [ [{"schema": "pii_intent", "name": "Yes..."}, "Yes..."], ... ]
    Return the label string of the final entry, or None if empty.
    """
    if not label_entries:
        return None
    # Take the last entry (most recent selection)
    last = label_entries[-1]
    # last is [{"schema": ..., "name": ...}, "label_string"]
    if isinstance(last, list) and len(last) >= 2:
        return last[1]
    return None


def collate(annotation_dir, data_jsonl, output_csv):
    data_index = load_data_index(data_jsonl)

    state_files = glob.glob(
        os.path.join(annotation_dir, "**", "user_state.json"), recursive=True
    )
    if not state_files:
        print(f"No user_state.json files found under {annotation_dir}")
        return

    fieldnames = [
        "annotator_id",
        "instance_id",
        "label",
        "user_query",
        "pii_units",
        "pii_gliner",
        "pii_gliner_types",
        "categorys_analysis",
    ]

    rows = []
    for path in sorted(state_files):
        annotator_id = os.path.basename(os.path.dirname(path))
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)

        label_map = state.get("instance_id_to_label_to_value", {})

        for instance_id, label_entries in label_map.items():
            label = extract_label(label_entries)
            data = data_index.get(str(instance_id), {})
            rows.append({
                "annotator_id": annotator_id,
                "instance_id": instance_id,
                "label": label,
                "user_query": data.get("user_query", ""),
                "pii_units": data.get("pii_units", ""),
                "pii_gliner": data.get("pii_gliner", ""),
                "pii_gliner_types": "|".join(data.get("pii_gliner_types", [])),
                "categorys_analysis": data.get("categorys_analysis", ""),
            })

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Written {len(rows)} rows from {len(state_files)} annotators → {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collate POTATO annotation results")
    parser.add_argument(
        "--annotation_dir",
        default="pupa_potato/annotation_output",
        help="Path to annotation_output directory",
    )
    parser.add_argument(
        "--data_jsonl",
        default="pupa_potato/data/potato_data.jsonl",
        help="Path to potato_data.jsonl",
    )
    parser.add_argument(
        "--output",
        default="annotations_collated.csv",
        help="Output CSV file path",
    )
    args = parser.parse_args()
    collate(args.annotation_dir, args.data_jsonl, args.output)
