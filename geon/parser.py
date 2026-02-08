"""Parse GEON text format into GeonPlace objects.

The parser handles the indentation-based hierarchy described in Section 8.1
of the spec, including:
- Top-level key: value pairs
- Lists (lines starting with ``-``)
- Nested key-value blocks
- Nested PLACE blocks inside CONTAINS
"""

from __future__ import annotations

import re
from typing import Any

from .models import Coordinate, Extent, GeonPlace

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

_COORD_RE = re.compile(
    r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$"
)


def _indent_level(line: str) -> int:
    """Return number of leading spaces."""
    return len(line) - len(line.lstrip(" "))


def _strip_list_marker(text: str) -> str:
    """Remove leading ``- `` from a list item."""
    stripped = text.lstrip()
    if stripped.startswith("- "):
        return stripped[2:]
    return stripped


def _parse_coordinate(text: str) -> Coordinate | None:
    m = _COORD_RE.match(text)
    if m:
        return Coordinate(lat=float(m.group(1)), lon=float(m.group(2)))
    return None


def _split_key_value(line: str) -> tuple[str, str] | None:
    """Split ``KEY: value`` — returns None when there is no colon."""
    stripped = line.strip()
    if ":" not in stripped:
        return None
    idx = stripped.index(":")
    key = stripped[:idx].strip()
    value = stripped[idx + 1:].strip()
    return key, value


# ---------------------------------------------------------------------------
# Block builder – turns lines into a tree of dicts / lists
# ---------------------------------------------------------------------------

def _tokenize_lines(text: str) -> list[tuple[int, str]]:
    """Return (indent, content) for each non-blank line."""
    results: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        results.append((_indent_level(raw), raw.strip()))
    return results


def _parse_block(lines: list[tuple[int, str]], start: int, base_indent: int) -> tuple[dict[str, Any], int]:
    """Recursively parse an indented block into a dict.

    Returns (parsed_dict, next_line_index).
    """
    result: dict[str, Any] = {}
    i = start
    while i < len(lines):
        indent, content = lines[i]
        if indent < base_indent:
            break

        if indent > base_indent:
            # Belongs to previous key – skip (handled below when key is set)
            i += 1
            continue

        kv = _split_key_value(content)
        if kv is None:
            # Plain text line at this level – skip
            i += 1
            continue

        key, value = kv

        if value:
            # Simple key: value on one line
            result[key] = value
            i += 1
        else:
            # Key with no inline value → children follow
            children, i = _collect_children(lines, i + 1, base_indent + 2)
            result[key] = children

    return result, i


def _collect_children(lines: list[tuple[int, str]], start: int, child_indent: int) -> tuple[Any, int]:
    """Collect the children of a key that had no inline value.

    Children may be a list (if they start with ``-``) or a dict of sub-keys.
    """
    if start >= len(lines):
        return [], start

    items: list[Any] = []
    mapping: dict[str, Any] = {}
    i = start
    is_list = False

    while i < len(lines):
        indent, content = lines[i]
        if indent < child_indent:
            break

        if indent == child_indent:
            if content.startswith("- "):
                is_list = True
                item_text = content[2:].strip()

                # Check if this list item is a nested PLACE block
                kv = _split_key_value(item_text)
                if kv and kv[0] == "PLACE":
                    # Nested GEON block – gather all indented lines under it
                    j = i + 1
                    while j < len(lines) and lines[j][0] > child_indent:
                        j += 1
                    # Determine the indent of nested fields so we can re-base to 0
                    child_lines = lines[i + 1:j]
                    if child_lines:
                        field_indent = child_lines[0][0]
                    else:
                        field_indent = child_indent + 2
                    rebased = [(0, item_text)] + [
                        (ind - field_indent, c) for ind, c in child_lines
                    ]
                    nested_block, _ = _parse_block(rebased, 0, 0)
                    items.append(nested_block)
                    i = j
                    continue
                else:
                    items.append(item_text)
                    i += 1
            else:
                kv = _split_key_value(content)
                if kv:
                    key, value = kv
                    if value:
                        mapping[key] = value
                        i += 1
                    else:
                        sub, i = _collect_children(lines, i + 1, child_indent + 2)
                        mapping[key] = sub
                else:
                    i += 1
        elif indent > child_indent:
            # Sub-children of the last list item – handle as nested block
            if is_list and items:
                sub_items: list[tuple[int, str]] = []
                j = i
                while j < len(lines) and lines[j][0] > child_indent:
                    sub_items.append(lines[j])
                    j += 1
                # Attach as dict to last list item
                if sub_items:
                    sub_block, _ = _parse_block(sub_items, 0, sub_items[0][0])
                    if isinstance(items[-1], str):
                        kv2 = _split_key_value(items[-1])
                        if kv2:
                            items[-1] = {kv2[0]: kv2[1], **sub_block}
                        else:
                            items[-1] = {"_value": items[-1], **sub_block}
                    elif isinstance(items[-1], dict):
                        items[-1].update(sub_block)
                i = j
            else:
                i += 1
        else:
            i += 1

    if is_list:
        return items, i
    if mapping:
        return mapping, i
    return items, i


# ---------------------------------------------------------------------------
# High-level: raw dict → GeonPlace
# ---------------------------------------------------------------------------

def _raw_to_place(raw: dict[str, Any]) -> GeonPlace:
    """Convert a raw parsed dict into a GeonPlace dataclass."""
    p = GeonPlace()

    p.place = raw.get("PLACE", "")
    p.type = raw.get("TYPE", "")
    p.id = raw.get("ID")

    # Location
    loc_str = raw.get("LOCATION", "")
    if loc_str:
        coord = _parse_coordinate(loc_str)
        if coord:
            p.location = coord

    # Boundary
    boundary_raw = raw.get("BOUNDARY", [])
    if isinstance(boundary_raw, list):
        for item in boundary_raw:
            text = item if isinstance(item, str) else str(item)
            coord = _parse_coordinate(text)
            if coord:
                p.boundary.append(coord)

    # Extent
    extent_str = raw.get("EXTENT", "")
    if extent_str:
        parts = [x.strip() for x in extent_str.split(",")]
        if len(parts) == 4:
            try:
                p.extent = Extent(
                    north=float(parts[0]),
                    south=float(parts[1]),
                    east=float(parts[2]),
                    west=float(parts[3]),
                )
            except ValueError:
                pass

    p.elevation = raw.get("ELEVATION")
    p.area = raw.get("AREA")

    # Purpose
    purpose_raw = raw.get("PURPOSE", [])
    if isinstance(purpose_raw, list):
        p.purpose = [str(x) for x in purpose_raw]
    elif isinstance(purpose_raw, str):
        p.purpose = [purpose_raw]

    # Experience
    exp_raw = raw.get("EXPERIENCE", {})
    if isinstance(exp_raw, dict):
        p.experience = {k: str(v) for k, v in exp_raw.items()}

    # Character
    char_raw = raw.get("CHARACTER", [])
    if isinstance(char_raw, list):
        p.character = [str(x) for x in char_raw]

    # Adjacencies
    adj_raw = raw.get("ADJACENCIES", [])
    if isinstance(adj_raw, list):
        p.adjacencies = [str(x) for x in adj_raw]

    # Connectivity
    conn_raw = raw.get("CONNECTIVITY", {})
    if isinstance(conn_raw, dict):
        p.connectivity = {k: _flatten_value(v) for k, v in conn_raw.items()}
    elif isinstance(conn_raw, list):
        p.connectivity = {str(i): str(x) for i, x in enumerate(conn_raw)}

    # Contains (nested places)
    contains_raw = raw.get("CONTAINS", [])
    if isinstance(contains_raw, list):
        for item in contains_raw:
            if isinstance(item, dict) and "PLACE" in item:
                p.contains.append(_raw_to_place(item))
            elif isinstance(item, str):
                child = GeonPlace(place=item)
                p.contains.append(child)

    p.part_of = raw.get("PART_OF")

    # Viewsheds
    vs_raw = raw.get("VIEWSHEDS", [])
    if isinstance(vs_raw, list):
        p.viewsheds = [str(x) if isinstance(x, str) else x for x in vs_raw]
    elif isinstance(vs_raw, dict):
        p.viewsheds = vs_raw

    # Temporal
    temp_raw = raw.get("TEMPORAL", {})
    if isinstance(temp_raw, dict):
        p.temporal = {k: _flatten_value(v) for k, v in temp_raw.items()}

    # Lifespan
    ls_raw = raw.get("LIFESPAN", {})
    if isinstance(ls_raw, dict):
        p.lifespan = {k: str(v) for k, v in ls_raw.items()}

    # Source
    src_raw = raw.get("SOURCE", [])
    if isinstance(src_raw, list):
        p.source = [str(x) for x in src_raw]
    elif isinstance(src_raw, str):
        p.source = [src_raw]

    # Confidence
    conf_raw = raw.get("CONFIDENCE", {})
    if isinstance(conf_raw, dict):
        p.confidence = {k: str(v) for k, v in conf_raw.items()}

    p.updated = raw.get("UPDATED")

    # Extended domain fields
    for field_name, attr in [
        ("BUILT_FORM", "built_form"),
        ("ECOLOGY", "ecology"),
        ("INFRASTRUCTURE", "infrastructure"),
        ("DEMOGRAPHICS", "demographics"),
        ("ECONOMY", "economy"),
        ("VISUAL", "visual"),
        ("VERTICAL_PROFILE", "vertical_profile"),
    ]:
        val = raw.get(field_name, {})
        if isinstance(val, dict):
            setattr(p, attr, {k: _flatten_value(v) for k, v in val.items()})

    # History
    hist_raw = raw.get("HISTORY", [])
    if isinstance(hist_raw, list):
        for item in hist_raw:
            if isinstance(item, dict):
                p.history.append(item)

    # Collect unknown fields into extra
    known = {
        "PLACE", "TYPE", "ID", "LOCATION", "BOUNDARY", "EXTENT", "ELEVATION",
        "AREA", "PURPOSE", "EXPERIENCE", "CHARACTER", "ADJACENCIES",
        "CONNECTIVITY", "CONTAINS", "PART_OF", "VIEWSHEDS", "TEMPORAL",
        "LIFESPAN", "SOURCE", "CONFIDENCE", "UPDATED", "BUILT_FORM",
        "ECOLOGY", "INFRASTRUCTURE", "DEMOGRAPHICS", "ECONOMY", "VISUAL",
        "HISTORY", "VERTICAL_PROFILE",
    }
    for k, v in raw.items():
        if k not in known:
            p.extra[k] = v

    return p


def _flatten_value(v: Any) -> Any:
    """Flatten simple wrappers so connectivity/temporal dicts stay readable."""
    if isinstance(v, list) and len(v) == 1 and isinstance(v[0], str):
        return v[0]
    return v


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(text: str) -> GeonPlace:
    """Parse a GEON text document into a :class:`GeonPlace`.

    >>> from geon import parse
    >>> p = parse("PLACE: My Park\\nTYPE: public_space\\nLOCATION: 51.5, -0.1")
    >>> p.place
    'My Park'
    """
    tokens = _tokenize_lines(text)
    if not tokens:
        return GeonPlace()
    raw, _ = _parse_block(tokens, 0, 0)
    return _raw_to_place(raw)


def parse_many(text: str) -> list[GeonPlace]:
    """Parse a multi-document GEON text (documents separated by blank lines
    where a new top-level PLACE: starts) into a list of :class:`GeonPlace`.
    """
    chunks: list[str] = []
    current_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("PLACE:") and _indent_level(line) == 0 and current_lines:
            chunks.append("\n".join(current_lines))
            current_lines = []
        current_lines.append(line)

    if current_lines:
        chunks.append("\n".join(current_lines))

    return [parse(chunk) for chunk in chunks]
