<p align="center"><img src="assets/logo.png" alt="GEON logo" width="280"></p>

# GEON — Geospatial Experience-Oriented Notation

**A human and LLM-readable format for spatial intelligence.**

GEON is a text-based format that bridges the gap between machine-optimized geospatial data (GeoJSON, WKT, Shapefiles) and human-readable spatial descriptions. It embeds semantic meaning, experiential qualities, and spatial relationships directly alongside geometric data — making it ideal for LLM reasoning about place.

```
PLACE: Nottingham Market Square
TYPE: public_space
LOCATION: 52.9548, -1.1581
AREA: 22000 sqm
PURPOSE:
  - civic gathering
  - events and festivals
  - informal commerce
EXPERIENCE:
  openness: high
  enclosure: medium
  activity_density: variable
ADJACENCIES:
  - Council House (immediate west)
  - Exchange Arcade (southeast corner)
TEMPORAL:
  weekday_footfall: 2000-3000 people/hour
  weekend_events: 2-3 per month
```

## Why GEON?

| | GeoJSON | GEON |
|---|---------|------|
| **Readability** | Machine-first | Human & LLM-first |
| **Semantics** | Flat properties bag | Structured semantic fields |
| **Experience** | Absent | Core feature (openness, safety, noise...) |
| **Relationships** | Requires computation | Explicit (adjacencies, connectivity) |
| **Temporal** | Limited | Integrated (footfall, events, seasons) |
| **Token efficiency** | ~24% more tokens | Baseline |

## Installation

```bash
pip install -e .

# With optional dependencies:
pip install -e ".[all]"      # requests + tiktoken
pip install -e ".[osm]"      # requests (for OSM examples)
pip install -e ".[tokens]"   # tiktoken (for token counting)
```

## Quick Start

```python
import geon

# Parse GEON text
place = geon.parse("""
PLACE: Victoria Park
TYPE: public_space
LOCATION: 52.9403, -1.1340
PURPOSE:
  - recreation
  - ecology
""")

print(place.place)      # "Victoria Park"
print(place.purpose)    # ["recreation", "ecology"]

# Generate GEON text
text = geon.generate(place)

# Validate
result = geon.validate(place)
print(result.valid)     # True

# Convert to/from GeoJSON
geojson = geon.to_geojson(place)
place2 = geon.from_geojson(geojson)
```

## Library API

### Core Models

```python
from geon import GeonPlace, Coordinate, Extent

place = GeonPlace(
    place="My Park",
    type="public_space",
    location=Coordinate(lat=51.5, lon=-0.1),
    purpose=["recreation", "ecology"],
    experience={"openness": "high", "activity_density": "moderate"},
)
```

### Parse & Generate

```python
import geon

# Single document
place = geon.parse(text)

# Multiple documents (separated by blank lines + new PLACE:)
places = geon.parse_many(multi_doc_text)

# Generate GEON text
text = geon.generate(place)
```

### Validate

```python
result = geon.validate(place)

result.valid      # True if no ERROR-level issues
result.errors     # List of ERROR issues
result.warnings   # List of WARNING issues
result.issues     # All issues (ERROR + WARNING + INFO)
```

Checks performed:
- Required fields present (`PLACE`, `TYPE`, `LOCATION`)
- Coordinate range correctness (lat +-90, lon +-180)
- Controlled vocabulary compliance for `TYPE` and `EXPERIENCE`
- Boundary polygon closure
- Recommended field presence (INFO level)
- Recursive validation of nested `CONTAINS` places

### Convert

```python
import geon

# GeoJSON -> GEON
place = geon.from_geojson(geojson_dict)          # Feature or FeatureCollection
place = geon.from_geojson_string(json_string)

# GEON -> GeoJSON
geojson = geon.to_geojson(place)                  # Feature dict
geojson = geon.to_geojson_collection(places)      # FeatureCollection dict
json_str = geon.to_geojson_string(place, indent=2)
```

The converter auto-infers GEON `TYPE` from common OSM/GeoJSON properties (`building`, `highway`, `railway`, `leisure`, `amenity`, `natural`, etc.).

### Controlled Vocabularies

```python
from geon import PLACE_TYPES, EXPERIENCE_SCALES, PURPOSE_CATEGORIES, ALL_PURPOSES

PLACE_TYPES
# {'public_space', 'street', 'building', 'transport_hub', 'infrastructure',
#  'natural_feature', 'district', 'landmark', 'threshold', 'hybrid'}

EXPERIENCE_SCALES['openness']
# ('very_low', 'low', 'medium', 'high', 'very_high')

EXPERIENCE_SCALES['noise_level']
# ('very_quiet', 'quiet', 'moderate', 'loud', 'very_loud')
```

## Web Demo

Open `web/index.html` in a browser for an interactive demo:

- **Click Map** — click anywhere to fetch nearby OSM features via Overpass API
- **Search OSM** — search by name using Nominatim
- **Paste GeoJSON** — paste or drag-and-drop any GeoJSON file
- **Output** — see generated GEON with syntax highlighting, GeoJSON, and token comparison

No server required — runs entirely in the browser.

## Examples

| Example | Description |
|---------|-------------|
| [`01_basic_usage.py`](examples/01_basic_usage.py) | Create, generate, parse, validate, round-trip to GeoJSON |
| [`02_from_geojson.py`](examples/02_from_geojson.py) | Convert Point, Polygon, and FeatureCollection |
| [`03_from_osm.py`](examples/03_from_osm.py) | Fetch POIs and polygons from OpenStreetMap (Overpass API) |
| [`04_from_overture.py`](examples/04_from_overture.py) | Convert Overture Maps features (categories, confidence, sources) |
| [`05_nested_places.py`](examples/05_nested_places.py) | Hierarchical CONTAINS — building with sub-places |
| [`06_parse_spec_example.py`](examples/06_parse_spec_example.py) | Parse the full Appendix A from the GEON spec |
| [`07_file_io.py`](examples/07_file_io.py) | Read and write `.geon` files |

Run any example:

```bash
python examples/01_basic_usage.py
```

## Token Analysis (examines/)

The `examines/` folder compares GEON against other formats for LLM efficiency:

| Script | What it measures |
|--------|-----------------|
| [`token_comparison.py`](examines/token_comparison.py) | Head-to-head: GEON vs GeoJSON vs WKT vs natural language |
| [`complexity_scaling.py`](examines/complexity_scaling.py) | How token counts scale from minimal to full-featured places |
| [`semantic_density.py`](examines/semantic_density.py) | Extractable facts per token across formats |

Key findings (with tiktoken/cl100k_base):

- **GEON uses ~24% fewer tokens** than pretty-printed GeoJSON for the same data
- **At minimal complexity**, GeoJSON is 2.9x larger due to structural overhead
- **GEON saves 23-37% on boundary vertices** (`- lat, lon` vs `[lon, lat],`)
- **Semantic density**: GEON encodes 8.8 facts per 100 tokens vs GeoJSON's 6.7
- **Context scaling**: ~1.2x more places fit in an LLM context window with GEON

```bash
pip install tiktoken   # for exact counts
python examines/token_comparison.py
```

## Project Structure

```
GEON/
  geon/                    # Python library
    __init__.py            # Public API
    models.py              # GeonPlace, Coordinate, Extent
    parser.py              # Parse GEON text -> objects
    generator.py           # Generate GEON text from objects
    validator.py           # Validation (errors, warnings, info)
    converter.py           # GeoJSON <-> GEON conversion
    vocab.py               # Controlled vocabularies
  web/
    index.html             # Interactive web demo (standalone)
  examples/                # Usage examples (Python)
  examines/                # Token count analysis scripts
  spec.md                  # GEON format specification v0.1.0
  pyproject.toml           # Package configuration
```

## GEON Format Reference

### Required Fields

| Field | Format | Example |
|-------|--------|---------|
| `PLACE` | Free text | `PLACE: Victoria Square` |
| `TYPE` | Controlled vocabulary | `TYPE: public_space` |
| `LOCATION` | `lat, lon` (WGS84) | `LOCATION: 52.4791, -1.9024` |

### Semantic Fields

| Field | Format |
|-------|--------|
| `PURPOSE` | List of activity types |
| `EXPERIENCE` | Key-value qualities (openness, noise, safety...) |
| `CHARACTER` | Descriptive list |

### Relational Fields

| Field | Format |
|-------|--------|
| `ADJACENCIES` | Named neighbours with distance/direction |
| `CONNECTIVITY` | Structured network descriptions |
| `CONTAINS` | Nested GEON blocks |
| `PART_OF` | Parent place reference |
| `VIEWSHEDS` | Visible landmarks |

### Temporal & Provenance

| Field | Format |
|-------|--------|
| `TEMPORAL` | Time-varying patterns |
| `SOURCE` | Data origin list |
| `CONFIDENCE` | Quality indicators |
| `UPDATED` | ISO 8601 timestamp |

See [`spec.md`](spec.md) for the complete specification.

## Author

**James Williams** — University of Nottingham

## License

GEON Specification: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
