"""Basic GEON usage: create, generate, parse, and validate.

No external dependencies required.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import geon

# ── 1. Build a GeonPlace programmatically ─────────────────────────────────

place = geon.GeonPlace(
    place="Nottingham Market Square",
    type="public_space",
    location=geon.Coordinate(52.9548, -1.1581),
    boundary=[
        geon.Coordinate(52.9553, -1.1592),
        geon.Coordinate(52.9553, -1.1570),
        geon.Coordinate(52.9543, -1.1570),
        geon.Coordinate(52.9543, -1.1592),
        geon.Coordinate(52.9553, -1.1592),
    ],
    area="22000 sqm",
    purpose=[
        "civic gathering",
        "events and festivals",
        "informal commerce",
        "circulation",
    ],
    experience={
        "openness": "high",
        "enclosure": "medium",
        "accessibility": "high",
        "activity_density": "variable",
    },
    adjacencies=[
        "Old Market Square tram stop (50m north)",
        "Council House (immediate west)",
        "Exchange Arcade (southeast corner)",
    ],
    connectivity={
        "pedestrian_entries": "6",
        "vehicular_access": "restricted",
        "public_transport": "tram (adjacent)",
    },
    temporal={
        "weekday_footfall": "2000-3000 people/hour",
        "weekend_events": "2-3 per month",
        "evening_activity": "low (20% of daytime)",
    },
)

# ── 2. Generate GEON text ─────────────────────────────────────────────────

text = geon.generate(place)
print("=== Generated GEON ===")
print(text)

# ── 3. Parse it back ──────────────────────────────────────────────────────

parsed = geon.parse(text)
print("=== Parsed back ===")
print(f"Place:    {parsed.place}")
print(f"Type:     {parsed.type}")
print(f"Location: {parsed.location}")
print(f"Purposes: {parsed.purpose}")
print()

# ── 4. Validate ───────────────────────────────────────────────────────────

result = geon.validate(parsed)
print("=== Validation ===")
print(f"Valid: {result.valid}")
for issue in result.issues:
    print(f"  {issue}")
print()

# ── 5. Round-trip to GeoJSON ──────────────────────────────────────────────

geojson = geon.to_geojson(parsed)
print("=== GeoJSON ===")
import json
print(json.dumps(geojson, indent=2))
