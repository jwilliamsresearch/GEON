"""Examine semantic density: how much *meaning* each format packs per token.

While token_comparison.py counts raw tokens, this script measures
how many distinct, extractable semantic facts each format encodes
and computes a "semantic density" score.

No external dependencies required (tiktoken optional for exact counts).
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


# ── Define semantic fact categories ───────────────────────────────────────

# Each "fact" is an independently useful piece of spatial information
# that an LLM could extract and reason about.

FACT_CATEGORIES = {
    "Identity":     ["name", "type", "id"],
    "Geometry":     ["location", "boundary", "area", "elevation"],
    "Purpose":      ["purpose_1", "purpose_2", "purpose_3", "purpose_4"],
    "Experience":   ["openness", "enclosure", "activity_density", "noise_level",
                     "visual_complexity", "sense_of_safety", "social_diversity"],
    "Character":    ["character_1", "character_2", "character_3"],
    "Relations":    ["adjacency_1", "adjacency_2", "adjacency_3", "adjacency_4",
                     "connectivity_ped", "connectivity_veh", "connectivity_cycle"],
    "Temporal":     ["footfall_weekday", "footfall_weekend", "seasonal_var"],
    "Provenance":   ["source_1", "source_2", "source_3",
                     "confidence_geom", "confidence_footfall", "confidence_exp",
                     "updated"],
}

TOTAL_FACTS = sum(len(v) for v in FACT_CATEGORIES.values())


# ── Representations ───────────────────────────────────────────────────────

# 1. GEON
GEON_TEXT = """\
PLACE: Victoria Square, Birmingham
TYPE: public_space
ID: bcc:vs-001
LOCATION: 52.4791, -1.9024
BOUNDARY:
  - 52.4795, -1.9030
  - 52.4795, -1.9018
  - 52.4787, -1.9018
  - 52.4787, -1.9030
  - 52.4795, -1.9030
AREA: 7500 sqm
ELEVATION: 150m above sea level
PURPOSE:
  - civic gathering
  - events and festivals
  - tourism
  - circulation
EXPERIENCE:
  openness: high
  enclosure: medium
  activity_density: moderate
  noise_level: moderate
  visual_complexity: high
  sense_of_safety: high (daytime), moderate (nighttime)
  social_diversity: high
CHARACTER:
  - historic (Victorian civic architecture)
  - prestigious (Council House, museum frontage)
  - transitional (connects New Street to Colmore Row)
ADJACENCIES:
  - Council House (west)
  - Birmingham Museum & Art Gallery (north)
  - Chamberlain Square (east)
  - New Street (south)
CONNECTIVITY:
  pedestrian_entries: 5
  vehicular_access: emergency only
  cycling: dismount zone
TEMPORAL:
  weekday_footfall: 1000-2000 people/hour
  weekend_footfall: 2000-4000 people/hour
  seasonal_variation: +50% December (Christmas market)
SOURCE:
  - Birmingham City Council (2024)
  - OpenStreetMap (2025-01)
  - Field observation (2025-01-15)
CONFIDENCE:
  geometry: high (surveyed)
  footfall: medium (modeled)
  experience_qualities: medium (single visit)
UPDATED: 2025-01-15T10:00:00Z"""

# 2. GeoJSON equivalent
GEOJSON_OBJ = {
    "type": "Feature",
    "id": "bcc:vs-001",
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [-1.9030, 52.4795], [-1.9018, 52.4795],
            [-1.9018, 52.4787], [-1.9030, 52.4787],
            [-1.9030, 52.4795],
        ]],
    },
    "properties": {
        "name": "Victoria Square, Birmingham",
        "type": "public_space",
        "area": "7500 sqm",
        "elevation": "150m above sea level",
        "purpose": ["civic gathering", "events and festivals", "tourism", "circulation"],
        "experience": {
            "openness": "high", "enclosure": "medium",
            "activity_density": "moderate", "noise_level": "moderate",
            "visual_complexity": "high",
            "sense_of_safety": "high (daytime), moderate (nighttime)",
            "social_diversity": "high",
        },
        "character": [
            "historic (Victorian civic architecture)",
            "prestigious (Council House, museum frontage)",
            "transitional (connects New Street to Colmore Row)",
        ],
        "adjacencies": [
            "Council House (west)",
            "Birmingham Museum & Art Gallery (north)",
            "Chamberlain Square (east)",
            "New Street (south)",
        ],
        "connectivity": {
            "pedestrian_entries": "5",
            "vehicular_access": "emergency only",
            "cycling": "dismount zone",
        },
        "temporal": {
            "weekday_footfall": "1000-2000 people/hour",
            "weekend_footfall": "2000-4000 people/hour",
            "seasonal_variation": "+50% December (Christmas market)",
        },
        "source": [
            "Birmingham City Council (2024)",
            "OpenStreetMap (2025-01)",
            "Field observation (2025-01-15)",
        ],
        "confidence": {
            "geometry": "high (surveyed)",
            "footfall": "medium (modeled)",
            "experience_qualities": "medium (single visit)",
        },
        "updated": "2025-01-15T10:00:00Z",
    },
}
GEOJSON_TEXT = json.dumps(GEOJSON_OBJ, indent=2)

# 3. OSM-style tags (flat key-value)
OSM_TAGS = """\
name=Victoria Square, Birmingham
leisure=park
ref=bcc:vs-001
addr:city=Birmingham
area=7500
ele=150
description=Civic gathering space with Victorian architecture
opening_hours=24/7
source=survey;OSM;fieldwork
note=Moderate activity, high openness, safe daytime"""

# 4. CSV row (how tabular GIS data is often shared)
CSV_ROW = """\
id,name,type,lat,lon,area_sqm,elevation_m,purpose,character
bcc:vs-001,"Victoria Square, Birmingham",public_space,52.4791,-1.9024,7500,150,"civic gathering;events;tourism;circulation","historic;prestigious;transitional"
"""


# ── Analysis ──────────────────────────────────────────────────────────────

representations = [
    ("GEON",           GEON_TEXT,    TOTAL_FACTS),
    ("GeoJSON",        GEOJSON_TEXT, TOTAL_FACTS),
    ("OSM tags",       OSM_TAGS,     12),  # OSM tags are inherently lossy for experience/temporal
    ("CSV row",        CSV_ROW,       9),  # CSV loses most semantic structure
]

print("=" * 80)
print("SEMANTIC DENSITY ANALYSIS")
print(f"Tokenizer: {TOKEN_METHOD}")
print(f"Total extractable facts in source data: {TOTAL_FACTS}")
print("=" * 80)
print()

# Fact category breakdown
print("FACT CATEGORIES:")
for cat, facts in FACT_CATEGORIES.items():
    print(f"  {cat:<14} {len(facts):>2} facts: {', '.join(facts)}")
print(f"  {'TOTAL':<14} {TOTAL_FACTS:>2}")
print()

# Comparison table
print(f"{'Format':<14} {'Tokens':>8} {'Facts':>7} {'Tok/fact':>9} {'Semantic':>10} {'Structured':>11}")
print(f"{'':14} {'':>8} {'':>7} {'':>9} {'density':>10} {'':>11}")
print("-" * 70)

for name, text, facts in representations:
    tokens = count_tokens(text)
    tpf = tokens / facts if facts else 0
    density = facts / tokens * 100 if tokens else 0  # facts per 100 tokens
    structured = "Yes" if name in ("GEON", "GeoJSON") else "Partial"
    print(f"{name:<14} {tokens:>8} {facts:>7} {tpf:>9.1f} {density:>9.1f}% {structured:>11}")

print()
print("-" * 70)
print()
print("INTERPRETATION:")
print()
print("  Semantic density = extractable facts per 100 tokens")
print()
print("  Higher is better: more spatial intelligence per token spent.")
print()
print("  GEON achieves the highest semantic density among structured formats")
print("  because its syntax overhead is minimal (no braces, no quotes on keys,")
print("  no commas between values).")
print()
print("  OSM tags are compact but LOSSY — they cannot represent experiential")
print("  qualities, temporal patterns, or confidence levels in their standard")
print("  tag schema.")
print()
print("  CSV is the most compact per-row but DESTROYS hierarchical structure,")
print("  loses most semantic fields, and requires external schema documentation.")
