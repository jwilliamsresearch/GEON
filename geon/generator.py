"""Generate GEON text from GeonPlace objects."""

from __future__ import annotations

from typing import Any

from .models import Coordinate, GeonPlace

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_INDENT = "  "


def _line(key: str, value: str, depth: int = 0) -> str:
    prefix = _INDENT * depth
    return f"{prefix}{key}: {value}\n"


def _section_header(key: str, depth: int = 0) -> str:
    prefix = _INDENT * depth
    return f"{prefix}{key}:\n"


def _list_items(items: list[str], depth: int = 1) -> str:
    prefix = _INDENT * depth
    return "".join(f"{prefix}- {item}\n" for item in items)


def _dict_items(mapping: dict[str, Any], depth: int = 1) -> str:
    """Render a dict of key: value pairs, recursing for nested dicts/lists."""
    buf = ""
    prefix = _INDENT * depth
    for k, v in mapping.items():
        if isinstance(v, dict):
            buf += f"{prefix}{k}:\n"
            buf += _dict_items(v, depth + 1)
        elif isinstance(v, list):
            buf += f"{prefix}{k}:\n"
            for item in v:
                if isinstance(item, dict):
                    # first key-value on the ``- `` line, rest indented
                    items_iter = iter(item.items())
                    first_k, first_v = next(items_iter)
                    buf += f"{_INDENT * (depth + 1)}- {first_k}: {first_v}\n"
                    for sub_k, sub_v in items_iter:
                        buf += f"{_INDENT * (depth + 2)}{sub_k}: {sub_v}\n"
                else:
                    buf += f"{_INDENT * (depth + 1)}- {item}\n"
        else:
            buf += f"{prefix}{k}: {v}\n"
    return buf


# ---------------------------------------------------------------------------
# Nested place
# ---------------------------------------------------------------------------

def _generate_nested(place: GeonPlace, depth: int) -> str:
    """Generate GEON text for a place nested inside CONTAINS."""
    prefix = _INDENT * depth
    buf = f"{prefix}- PLACE: {place.place}\n"
    inner = depth + 2  # align under the ``- ``

    if place.type:
        buf += _line("TYPE", place.type, inner)
    if place.location:
        buf += _line("LOCATION", str(place.location), inner)
    if place.area:
        buf += _line("AREA", place.area, inner)

    if place.purpose:
        if len(place.purpose) == 1:
            buf += _line("PURPOSE", place.purpose[0], inner)
        else:
            buf += _section_header("PURPOSE", inner)
            buf += _list_items(place.purpose, inner + 1)

    if place.temporal:
        buf += _section_header("TEMPORAL", inner)
        buf += _dict_items(place.temporal, inner + 1)

    if place.experience:
        buf += _section_header("EXPERIENCE", inner)
        buf += _dict_items(place.experience, inner + 1)

    return buf


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate(place: GeonPlace) -> str:
    """Serialize a :class:`GeonPlace` to GEON text format.

    >>> from geon.models import GeonPlace, Coordinate
    >>> p = GeonPlace(place="My Park", type="public_space",
    ...               location=Coordinate(51.5, -0.1))
    >>> print(generate(p))
    PLACE: My Park
    TYPE: public_space
    LOCATION: 51.5, -0.1
    <BLANKLINE>
    """
    buf = ""

    # --- Identity ---
    buf += _line("PLACE", place.place)
    buf += _line("TYPE", place.type)
    if place.id:
        buf += _line("ID", place.id)

    # --- Geometry ---
    if place.location:
        buf += _line("LOCATION", str(place.location))
    if place.boundary:
        buf += _section_header("BOUNDARY")
        buf += _list_items([str(c) for c in place.boundary])
    if place.extent:
        buf += _line("EXTENT", str(place.extent))
    if place.elevation:
        buf += _line("ELEVATION", place.elevation)
    if place.area:
        buf += _line("AREA", place.area)

    # --- Semantic ---
    if place.purpose:
        buf += _section_header("PURPOSE")
        buf += _list_items(place.purpose)
    if place.experience:
        buf += _section_header("EXPERIENCE")
        buf += _dict_items(place.experience)
    if place.character:
        buf += _section_header("CHARACTER")
        buf += _list_items(place.character)

    # --- Relational ---
    if place.adjacencies:
        buf += _section_header("ADJACENCIES")
        buf += _list_items(place.adjacencies)
    if place.connectivity:
        buf += _section_header("CONNECTIVITY")
        buf += _dict_items(place.connectivity)
    if place.contains:
        buf += _section_header("CONTAINS")
        for child in place.contains:
            buf += _generate_nested(child, depth=1)
            buf += "\n"
    if place.part_of:
        buf += _line("PART_OF", place.part_of)
    if place.viewsheds:
        buf += _section_header("VIEWSHEDS")
        if isinstance(place.viewsheds, list):
            buf += _list_items([str(v) for v in place.viewsheds])
        elif isinstance(place.viewsheds, dict):
            buf += _dict_items(place.viewsheds)

    # --- Temporal ---
    if place.temporal:
        buf += _section_header("TEMPORAL")
        buf += _dict_items(place.temporal)
    if place.lifespan:
        buf += _section_header("LIFESPAN")
        buf += _dict_items(place.lifespan)

    # --- Provenance ---
    if place.source:
        buf += _section_header("SOURCE")
        buf += _list_items(place.source)
    if place.confidence:
        buf += _section_header("CONFIDENCE")
        buf += _dict_items(place.confidence)
    if place.updated:
        buf += _line("UPDATED", place.updated)

    # --- Extended ---
    for field_name, attr in [
        ("BUILT_FORM", "built_form"),
        ("ECOLOGY", "ecology"),
        ("INFRASTRUCTURE", "infrastructure"),
        ("DEMOGRAPHICS", "demographics"),
        ("ECONOMY", "economy"),
        ("VISUAL", "visual"),
        ("VERTICAL_PROFILE", "vertical_profile"),
    ]:
        data = getattr(place, attr, {})
        if data:
            buf += _section_header(field_name)
            buf += _dict_items(data)

    if place.history:
        buf += _section_header("HISTORY")
        for entry in place.history:
            buf += _dict_items(entry)

    # --- Extra / unknown fields ---
    for key, value in place.extra.items():
        if isinstance(value, dict):
            buf += _section_header(key)
            buf += _dict_items(value)
        elif isinstance(value, list):
            buf += _section_header(key)
            buf += _list_items([str(v) for v in value])
        else:
            buf += _line(key, str(value))

    return buf
