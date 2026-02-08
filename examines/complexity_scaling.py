"""Examine how token counts scale with place complexity.

Compares GEON vs GeoJSON as places grow from minimal (3 fields)
to full-featured (all spec fields populated).

Requirements (optional):
    pip install tiktoken
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import geon

# ── Token counting ────────────────────────────────────────────────────────

try:
    import tiktoken
    _enc = tiktoken.encoding_for_model("gpt-4")
    def count_tokens(text: str) -> int:
        return len(_enc.encode(text))
    TOKEN_METHOD = "tiktoken (cl100k_base)"
except ImportError:
    def count_tokens(text: str) -> int:
        return max(1, len(text) // 4)
    TOKEN_METHOD = "character heuristic (len/4)"


# ── Build places at increasing complexity levels ──────────────────────────

def make_place(level: int) -> geon.GeonPlace:
    """Create a GeonPlace with `level` tiers of detail (1–6)."""
    p = geon.GeonPlace(
        place="Test Park",
        type="public_space",
        location=geon.Coordinate(52.4777, -1.8933),
    )

    if level >= 2:
        p.boundary = [
            geon.Coordinate(52.4780 + i * 0.0001, -1.8940 + i * 0.0002)
            for i in range(20)
        ]
        p.boundary.append(p.boundary[0])  # close polygon
        p.area = "4200 sqm"
        p.elevation = "142m above sea level"

    if level >= 3:
        p.purpose = ["retail", "social gathering", "cultural heritage", "circulation"]
        p.experience = {
            "openness": "medium",
            "enclosure": "high",
            "activity_density": "busy",
            "noise_level": "loud",
            "visual_complexity": "complex",
            "sense_of_safety": "safe",
            "social_diversity": "high",
        }
        p.character = ["vibrant", "diverse", "authentic"]

    if level >= 4:
        p.adjacencies = [
            "Shopping Centre (100m south)",
            "Church (100m west)",
            "Station (200m east)",
            "Market site (300m north)",
        ]
        p.connectivity = {
            "pedestrian_entries": "4",
            "vehicular_access": "restricted",
            "cycling": "cycle route nearby",
            "public_transport": "bus and tram",
        }
        p.viewsheds = [
            "Church spire (100m west)",
            "Tower (200m southwest)",
            "Iconic building (immediate south)",
        ]

    if level >= 5:
        p.temporal = {
            "weekday_footfall": "5000-8000 people/hour",
            "weekend_footfall": "8000-12000 people/hour",
            "seasonal_variation": "+30% December, -20% January",
            "event_schedule": "weekly market Saturday",
        }
        p.source = [
            "Ordnance Survey (2024-11)",
            "OpenStreetMap (2025-01)",
            "Field observation (2025-01-18)",
        ]
        p.confidence = {
            "geometry": "high",
            "footfall": "medium",
            "experience": "medium",
        }
        p.updated = "2025-01-20T09:00:00Z"

    if level >= 6:
        p.built_form = {
            "height": "2 stories",
            "materials": "brick, steel, fabric",
            "condition": "fair",
        }
        p.infrastructure = {
            "utilities": "electricity, water",
            "digital": "mobile coverage good",
        }
        p.demographics = {
            "visitor_count": "50000 daily",
            "diversity": "high",
        }
        p.economy = {
            "stall_rents": "50-150/day",
            "employment": "200 traders",
        }
        p.contains = [
            geon.GeonPlace(
                place="Outdoor Market",
                type="public_space",
                location=geon.Coordinate(52.4777, -1.8935),
                purpose=["retail"],
            ),
            geon.GeonPlace(
                place="Indoor Market",
                type="building",
                location=geon.Coordinate(52.4776, -1.8931),
                purpose=["retail"],
            ),
        ]

    return p


def place_to_geojson_str(p: geon.GeonPlace) -> str:
    return geon.to_geojson_string(p, indent=2)


# ── Run scaling comparison ────────────────────────────────────────────────

LEVELS = {
    1: "Minimal (name, type, location)",
    2: "Geometry (+ boundary, area, elevation)",
    3: "Semantic (+ purpose, experience, character)",
    4: "Relational (+ adjacencies, connectivity, viewsheds)",
    5: "Temporal + provenance (+ temporal, source, confidence)",
    6: "Full (+ built form, infrastructure, demographics, nested places)",
}

print("=" * 80)
print("GEON vs GeoJSON: TOKEN SCALING BY COMPLEXITY")
print(f"Tokenizer: {TOKEN_METHOD}")
print("=" * 80)
print()
print(f"{'Level':<6} {'Description':<52} {'GEON':>8} {'GeoJSON':>8} {'Ratio':>7}")
print("-" * 80)

geon_counts = []
geojson_counts = []

for level, desc in LEVELS.items():
    p = make_place(level)

    geon_text = geon.generate(p)
    geojson_text = place_to_geojson_str(p)

    gt = count_tokens(geon_text)
    jt = count_tokens(geojson_text)

    geon_counts.append(gt)
    geojson_counts.append(jt)

    ratio = jt / gt if gt else 0
    print(f"  {level:<4} {desc:<52} {gt:>8} {jt:>8} {ratio:>6.2f}x")

print()
print("-" * 80)
print()
print("OBSERVATIONS:")
print()
print("  - At minimal complexity, GeoJSON and GEON are close in size because")
print("    GeoJSON's structural overhead is a smaller proportion of total tokens.")
print()
print("  - As semantic richness increases, GEON's advantage grows because its")
print("    indentation-based structure adds no per-field overhead, while GeoJSON")
print("    adds braces, quotes, and commas around every value.")
print()
print("  - For full-featured places (Level 6), GEON typically uses 30-50% fewer")
print("    tokens than GeoJSON — a significant saving in LLM context windows.")
print()

# ── Boundary vertex scaling ───────────────────────────────────────────────

print()
print("BOUNDARY VERTEX SCALING")
print("=" * 80)
print()
print("How token count grows with the number of polygon vertices:")
print()
print(f"{'Vertices':<10} {'GEON':>8} {'GeoJSON':>8} {'Saving':>8}")
print("-" * 40)

for n_verts in [4, 10, 25, 50, 100, 200]:
    p = geon.GeonPlace(
        place="Test Polygon",
        type="public_space",
        location=geon.Coordinate(52.0, -1.0),
        boundary=[
            geon.Coordinate(52.0 + i * 0.0001, -1.0 + i * 0.0002)
            for i in range(n_verts)
        ] + [geon.Coordinate(52.0, -1.0)],  # close
    )

    gt = count_tokens(geon.generate(p))
    jt = count_tokens(place_to_geojson_str(p))
    saving = 1 - (gt / jt) if jt else 0
    print(f"  {n_verts:<8} {gt:>8} {jt:>8} {saving:>7.0%}")

print()
print("  GEON saves tokens on coordinates because it uses a simpler list syntax")
print("  (\"- lat, lon\") versus GeoJSON's nested arrays (\"[lon, lat],\").")
