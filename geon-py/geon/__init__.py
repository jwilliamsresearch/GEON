"""GEON — Geospatial Experience-Oriented Notation.

A human and LLM-readable format for spatial intelligence.

Quick start::

    import geon

    # Parse GEON text
    place = geon.parse(text)

    # Generate GEON text
    text = geon.generate(place)

    # Convert from GeoJSON
    place = geon.from_geojson(geojson_dict)

    # Convert to GeoJSON
    geojson = geon.to_geojson(place)

    # Validate
    result = geon.validate(place)
    print(result.valid)
"""

__version__ = "0.1.0"

from .converter import (
    from_geojson,
    from_geojson_string,
    to_geojson,
    to_geojson_collection,
    to_geojson_string,
)
from .generator import generate
from .models import Coordinate, Extent, GeonPlace
from .parser import parse, parse_many
from .validator import Issue, Severity, ValidationResult, validate
from .vocab import (
    ALL_PURPOSES,
    EXPERIENCE_SCALES,
    PLACE_TYPES,
    PURPOSE_CATEGORIES,
)

__all__ = [
    # Core models
    "GeonPlace",
    "Coordinate",
    "Extent",
    # Parse / generate
    "parse",
    "parse_many",
    "generate",
    # Conversion
    "from_geojson",
    "from_geojson_string",
    "to_geojson",
    "to_geojson_collection",
    "to_geojson_string",
    # Validation
    "validate",
    "ValidationResult",
    "Issue",
    "Severity",
    # Vocabularies
    "PLACE_TYPES",
    "EXPERIENCE_SCALES",
    "PURPOSE_CATEGORIES",
    "ALL_PURPOSES",
]
