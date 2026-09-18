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

    # Give Bylaws search results meaningful titles.
    #
    # Quarto has already placed the navigation hierarchy in "crumbs",
    # for example ["Bylaws", "Definitions"].
    crumbs = record.get("crumbs") or []

    if base_href.startswith("Bylaws/"):
        if crumbs:
            page_name = crumbs[-1]

            if page_name == "Bylaws":
                record["title"] = "Bylaws"
            else:
                record["title"] = f"Bylaws: {page_name}"
        else:
            record["title"] = "Bylaws"

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

    previous_has_anchor = "#" in previous.get("href", "")
    current_has_anchor = "#" in href

    # For otherwise identical records, prefer the URL without an anchor.
    #
    # Quarto adds ?q=SEARCH-TERMS when a result is selected. Without a
    # section anchor, the browser can scroll to the first highlighted
    # occurrence. With an anchor, it scrolls to the section heading instead.
    if previous_has_anchor and not current_has_anchor:
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
    f"Search-index processing complete: "
    f"{len(records)} records -> {len(deduplicated)} records "
    f"({removed} duplicates removed)."
)