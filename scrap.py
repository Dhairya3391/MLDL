import requests
from bs4 import BeautifulSoup

url = "https://darshan.ac.in/placement/list/btech-computer/2026"

# Fetch and parse the page
resp = requests.get(url, timeout=30)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

placements = []

for card in soup.select("h2"):
    name = card.get_text(strip=True)

    parts = []
    sib = card.find_next_sibling()
    while sib and sib.name != "h2":
        text = sib.get_text(" ", strip=True)
        if text:
            parts.append(text)
        sib = sib.find_next_sibling()

    if "CTC per Annum" not in parts or "Placed in" not in parts:
        continue

    entry = {"name": name}

    if parts and parts[0].isdigit():
        entry["roll"] = parts[0]

    try:
        ctc_idx = parts.index("CTC per Annum") + 1
        entry["ctc"] = parts[ctc_idx]
    except (ValueError, IndexError):
        entry["ctc"] = ""

    placement_type = ""
    city = ""
    try:
        place_idx = parts.index("Placed in")
        after = parts[place_idx + 1 : place_idx + 3]
        if after:
            if after[0] == "Self Placed":
                placement_type = "Self Placed"
                city = after[1] if len(after) > 1 else ""
            else:
                city = after[0]
    except ValueError:
        pass

    entry["placement_type"] = placement_type
    entry["city"] = city
    placements.append(entry)

if not placements:
    print("No placement data found.")
    raise SystemExit

fields = ["name", "roll", "ctc", "placement_type", "city"]
headers = ["Name", "Roll", "CTC", "Placement", "City"]

# Compute column widths for a clean table
col_widths = []
for field, header in zip(fields, headers):
    longest = max(len(str(row.get(field, ""))) for row in placements)
    col_widths.append(max(longest, len(header)))


def fmt_row(values):
    return " | ".join(str(val).ljust(width) for val, width in zip(values, col_widths))


print(fmt_row(headers))
print("-+-".join("-" * width for width in col_widths))

for row in placements:
    ordered = [row.get(field, "") for field in fields]
    print(fmt_row(ordered))