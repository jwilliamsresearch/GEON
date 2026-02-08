"""Demonstrate hierarchical / nested GEON places (Section 4.1).

Shows how to model a building that CONTAINS sub-places.
No external dependencies required.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import geon

# ── Build a nested place hierarchy ────────────────────────────────────────

grand_central = geon.GeonPlace(
    place="Grand Central Birmingham",
    type="building",
    location=geon.Coordinate(52.4774, -1.8984),
    area="75000 sqm",
    purpose=["retail", "transport", "food and beverage"],
    experience={
        "activity_density": "very_high",
        "noise_level": "loud",
        "legibility": "medium",
    },
    adjacencies=[
        "New Street Station (below)",
        "Bullring Shopping Centre (200m east)",
        "Victoria Square (300m north)",
    ],
    connectivity={
        "pedestrian_entries": "6",
        "rail": "New Street Station (direct access)",
        "public_transport": "tram (Corporation Street, 200m)",
    },
    contains=[
        geon.GeonPlace(
            place="John Lewis flagship store",
            type="building",
            location=geon.Coordinate(52.4776, -1.8983),
            area="25000 sqm",
            purpose=["retail (department store)"],
        ),
        geon.GeonPlace(
            place="Grand Central Shopping Centre",
            type="building",
            location=geon.Coordinate(52.4773, -1.8985),
            area="50000 sqm",
            purpose=["retail (mixed)", "food and beverage"],
            temporal={
                "trading_hours": "09:00-20:00 Mon-Sat, 11:00-17:00 Sun",
            },
        ),
    ],
    part_of="Birmingham City Centre",
    source=["Field observation (2025-01)", "OpenStreetMap (2025-01)"],
)

# ── Generate ──────────────────────────────────────────────────────────────

text = geon.generate(grand_central)
print("=== Nested GEON Document ===")
print(text)

# ── Parse it back and verify structure ────────────────────────────────────

parsed = geon.parse(text)
print(f"=== Parsed: {parsed.place} ===")
print(f"Contains {len(parsed.contains)} sub-places:")
for child in parsed.contains:
    print(f"  - {child.place} ({child.type})")
print()

# ── Validate (including children) ─────────────────────────────────────────

result = geon.validate(parsed)
print(f"Valid: {result.valid}")
for issue in result.issues:
    print(f"  {issue}")
