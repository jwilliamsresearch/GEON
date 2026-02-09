# GEON for Python (`geon-py`)

A robust, reference implementation of **GEON (Geospatial Experience-Oriented Notation)** for Python 3.8+.

## Overview

`geon-py` is the reference parser and generator for the GEON format. It is designed for:
- **Data Science**: Easily converting between GeoJSON/Pandas workflows and GEON for Analysis.
- **LLM Integration**: Generating prompt-ready spatial descriptions.
- **Validation**: Ensuring data integrity against the GEON specification.

## Installation

```bash
pip install -e .
```

### Optional Dependencies
- `.[osm]`: Adds `requests` for fetching OpenStreetMap data (used in examples).
- `.[tokens]`: Adds `tiktoken` for token usage analysis.

## Core API Reference

### `geon.parse(text: str) -> GeonPlace`
Parses a GEON-formatted string into a `GeonPlace` object.

```python
import geon

text = """
PLACE: Central Park
TYPE: public_space
LOCATION: 40.7851, -73.9683
"""
place = geon.parse(text)
```

**Exceptions:**
- `ValueError`: Raised if indentation is malformed or critical syntax is broken.

---

### `geon.generate(place: GeonPlace) -> str`
Generates a deterministic, properly indented GEON string from a `GeonPlace` object.

```python
print(geon.generate(place))
# PLACE: Central Park
# TYPE: public_space
# ...
```

---

### `geon.validate(place: GeonPlace) -> ValidationResult`
Validates the object against the GEON specification.

```python
result = geon.validate(place)
if not result.valid:
    for error in result.errors:
        print(f"Error: {error}")
```

**Validation Checks:**
- Presence of mandatory fields (`PLACE`, `TYPE`, `LOCATION`).
- Coordinate bounds (Lat: -90..90, Lon: -180..180).
- Controlled vocabulary compliance (e.g., `TYPE` must be a known GEON type).
- Geometry validity (e.g., Polygon closure).

---

### `geon.from_geojson(data: dict | str) -> GeonPlace | List[GeonPlace]`
Converts GeoJSON Feature or FeatureCollection into GEON objects.

- **Auto-inference**: Infers `TYPE` from OSM tags (`amenity`, `leisure`, etc.).
- **Centroid**: Calculates `LOCATION` centroid for Polygons automatically.

---

## Data Model (`GeonPlace`)

The `GeonPlace` class maps directly to the specification fields.

| Attribute | Type | Description |
|-----------|------|-------------|
| `place` | `str` | Name of the place (Required). |
| `type` | `str` | Category (e.g., `public_space`, `building`). |
| `location` | `Coordinate` | Centroid (lat, lon). |
| `boundary` | `List[Coordinate]` | Polygon vertices. |
| `purpose` | `List[str]` | List of functions/uses. |
| `experience` | `Dict[str, str]` | Qualities like `openness`, `noise_level`. |
| `adjacencies` | `List[str]` | Text descriptions of neighbors. |
| `contains` | `List[GeonPlace]` | Nested sub-places. |
| `extra` | `Dict[str, Any]` | Catch-all for unknown fields. |

## Development

### Running Tests
```bash
python -m unittest discover tests
```

### Project Structure
- `geon/parser.py`: Indentation-sensitive lines parser.
- `geon/generator.py`: Recursive object serializer.
- `geon/validator.py`: Logic for spec compliance.
- `geon/vocab.py`: Controlled vocabularies (Types, Experience scales).

## License
MIT License
