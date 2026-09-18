import json
from pathlib import Path

search_path = Path("_site/search.json")

if not search_path.exists():
    raise SystemExit(f"Search index not found: {search_path}")

records = json.loads(search_path.read_text(encoding="utf-8"))

deduplicated = []
positions = {}

for record in records:
    href = record.get("href", "")
    base_href = href.split("#", 1)[0]

    # Records are duplicates only when they belong to the same page and
    # contain exactly the same searchable title, section, and text.
    key = (
        base_href,
        record.get("title", ""),
        record.get("section", ""),
        record.get("text", ""),
    )

    if key not in positions:
        positions[key] = len(deduplicated)
        deduplicated.append(record)
        continue

    previous_position = positions[key]
    previous = deduplicated[previous_position]

    # Prefer the anchored version because selecting it takes the reader
    # directly to the matching policy heading.
    previous_has_anchor = "#" in previous.get("href", "")
    current_has_anchor = "#" in href

    if current_has_anchor and not previous_has_anchor:
        deduplicated[previous_position] = record

removed = len(records) - len(deduplicated)

search_path.write_text(
    json.dumps(
        deduplicated,
        ensure_ascii=False,
        separators=(",", ":"),
    ),
    encoding="utf-8",
)

print(
    f"Search-index deduplication complete: "
    f"{len(records)} records -> {len(deduplicated)} records "
    f"({removed} duplicates removed)."
)