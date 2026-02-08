"""Bi-directional conversion between GEON and GeoJSON (Section 5)."""

from __future__ import annotations

import json
from typing import Any

from .models import Coordinate, GeonPlace


# ---------------------------------------------------------------------------
# GeoJSON → GEON
# ---------------------------------------------------------------------------

# Mapping from common OSM/GeoJSON property keys to GEON TYPE values
_TYPE_MAPPING: dict[str, str] = {
    "park": "public_space",
    "garden": "public_space",
    "playground": "public_space",
    "plaza": "public_space",
    "square": "public_space",
    "common": "public_space",
    "pitch": "public_space",
    "marketplace": "public_space",
    "road": "street",
    "residential": "street",
    "primary": "street",
    "secondary": "street",
    "tertiary": "street",
    "footway": "street",
    "cycleway": "street",
    "path": "street",
    "pedestrian": "street",
    "motorway": "street",
    "trunk": "street",
    "railway_station": "transport_hub",
    "station": "transport_hub",
    "bus_station": "transport_hub",
    "airport": "transport_hub",
    "halt": "transport_hub",
    "ferry_terminal": "transport_hub",
    "yes": "building",
    "house": "building",
    "apartments": "building",
    "commercial": "building",
    "retail": "building",
    "industrial": "building",
    "office": "building",
    "church": "building",
    "cathedral": "building",
    "school": "building",
    "hospital": "building",
    "university": "building",
    "monument": "landmark",
    "memorial": "landmark",
    "statue": "landmark",
    "tower": "landmark",
    "bridge": "threshold",
    "river": "natural_feature",
    "stream": "natural_feature",
    "lake": "natural_feature",
    "wood": "natural_feature",
    "forest": "natural_feature",
    "peak": "natural_feature",
    "cliff": "natural_feature",
    "beach": "natural_feature",
    "wetland": "natural_feature",
}


def _infer_type(properties: dict[str, Any]) -> str:
    """Best-effort type inference from GeoJSON properties."""
    # Check explicit type/geon_type
    if "geon_type" in properties:
        return str(properties["geon_type"])

    # Check common OSM-style keys
    for key in ("type", "building", "highway", "railway", "leisure", "amenity",
                "natural", "landuse", "tourism", "man_made", "waterway"):
        val = properties.get(key, "")
        if val and str(val) in _TYPE_MAPPING:
            return _TYPE_MAPPING[str(val)]

    return "hybrid"


def _infer_name(properties: dict[str, Any]) -> str:
    for key in ("name", "name:en", "official_name", "alt_name", "title", "label"):
        if key in properties and properties[key]:
            return str(properties[key])
    return "Unnamed"


def _extract_centroid(geometry: dict[str, Any]) -> Coordinate | None:
    """Extract a representative point from GeoJSON geometry."""
    gtype = geometry.get("type", "")
    coords = geometry.get("coordinates")
    if not coords:
        return None

    if gtype == "Point":
        return Coordinate.from_geojson_position(coords)

    if gtype in ("MultiPoint", "LineString"):
        # Use midpoint of the coordinate list
        mid = coords[len(coords) // 2]
        return Coordinate.from_geojson_position(mid)

    if gtype == "Polygon":
        # Centroid of the exterior ring (simple average)
        ring = coords[0]
        avg_lon = sum(c[0] for c in ring) / len(ring)
        avg_lat = sum(c[1] for c in ring) / len(ring)
        return Coordinate(lat=avg_lat, lon=avg_lon)

    if gtype == "MultiPolygon":
        # Centroid of the first polygon
        ring = coords[0][0]
        avg_lon = sum(c[0] for c in ring) / len(ring)
        avg_lat = sum(c[1] for c in ring) / len(ring)
        return Coordinate(lat=avg_lat, lon=avg_lon)

    return None


def _extract_boundary(geometry: dict[str, Any]) -> list[Coordinate]:
    """Extract boundary coordinates from a Polygon geometry."""
    gtype = geometry.get("type", "")
    coords = geometry.get("coordinates")
    if gtype == "Polygon" and coords:
        return [Coordinate.from_geojson_position(c) for c in coords[0]]
    if gtype == "MultiPolygon" and coords:
        return [Coordinate.from_geojson_position(c) for c in coords[0][0]]
    return []


def _extract_purposes(properties: dict[str, Any]) -> list[str]:
    """Infer PURPOSE list from properties."""
    if "purpose" in properties:
        val = properties["purpose"]
        if isinstance(val, list):
            return [str(x) for x in val]
        return [str(val)]

    purposes: list[str] = []
    amenity = properties.get("amenity", "")
    if amenity:
        purposes.append(str(amenity))
    leisure = properties.get("leisure", "")
    if leisure:
        purposes.append(str(leisure))
    shop = properties.get("shop", "")
    if shop:
        purposes.append(f"retail ({shop})")
    return purposes


def from_geojson(geojson: dict[str, Any]) -> GeonPlace | list[GeonPlace]:
    """Convert a GeoJSON Feature or FeatureCollection to GEON.

    Returns a single :class:`GeonPlace` for a Feature, or a list for a
    FeatureCollection.
    """
    gtype = geojson.get("type", "")

    if gtype == "FeatureCollection":
        return [_feature_to_geon(f) for f in geojson.get("features", [])]

    if gtype == "Feature":
        return _feature_to_geon(geojson)

    raise ValueError(f"Unsupported GeoJSON type: {gtype}")


def _feature_to_geon(feature: dict[str, Any]) -> GeonPlace:
    props = feature.get("properties", {}) or {}
    geom = feature.get("geometry", {}) or {}

    p = GeonPlace()
    p.place = _infer_name(props)
    p.type = _infer_type(props)
    p.location = _extract_centroid(geom)
    p.boundary = _extract_boundary(geom)
    p.purpose = _extract_purposes(props)

    # Carry over experience if present
    if "experience" in props and isinstance(props["experience"], dict):
        p.experience = {k: str(v) for k, v in props["experience"].items()}

    # Carry over ID
    feat_id = feature.get("id") or props.get("id") or props.get("@id")
    if feat_id:
        p.id = str(feat_id)

    # Carry over source
    if "source" in props:
        val = props["source"]
        p.source = val if isinstance(val, list) else [str(val)]

    p.source.append("GeoJSON conversion")

    return p


def from_geojson_string(text: str) -> GeonPlace | list[GeonPlace]:
    """Parse a GeoJSON string and convert to GEON."""
    return from_geojson(json.loads(text))


# ---------------------------------------------------------------------------
# GEON → GeoJSON
# ---------------------------------------------------------------------------

def to_geojson(place: GeonPlace) -> dict[str, Any]:
    """Convert a :class:`GeonPlace` to a GeoJSON Feature dict.

    Geometry is derived from LOCATION (Point) or BOUNDARY (Polygon).
    Semantic fields are placed in ``properties``.
    """
    properties: dict[str, Any] = {
        "name": place.place,
        "geon_type": place.type,
    }

    if place.id:
        properties["id"] = place.id

    if place.purpose:
        properties["purpose"] = place.purpose
    if place.experience:
        properties["experience"] = place.experience
    if place.character:
        properties["character"] = place.character
    if place.adjacencies:
        properties["adjacencies"] = place.adjacencies
    if place.connectivity:
        properties["connectivity"] = place.connectivity
    if place.part_of:
        properties["part_of"] = place.part_of
    if place.temporal:
        properties["temporal"] = place.temporal
    if place.source:
        properties["source"] = place.source
    if place.confidence:
        properties["confidence"] = place.confidence
    if place.updated:
        properties["updated"] = place.updated
    if place.area:
        properties["area"] = place.area
    if place.elevation:
        properties["elevation"] = place.elevation

    # Extended fields
    for attr in ("built_form", "ecology", "infrastructure", "demographics", "economy"):
        data = getattr(place, attr, {})
        if data:
            properties[attr] = data

    # Geometry
    geometry: dict[str, Any]
    if place.boundary and len(place.boundary) >= 3:
        geometry = {
            "type": "Polygon",
            "coordinates": [[c.to_geojson_position() for c in place.boundary]],
        }
    elif place.location:
        geometry = {
            "type": "Point",
            "coordinates": place.location.to_geojson_position(),
        }
    else:
        geometry = {"type": "Point", "coordinates": [0, 0]}

    feature: dict[str, Any] = {
        "type": "Feature",
        "geometry": geometry,
        "properties": properties,
    }

    if place.id:
        feature["id"] = place.id

    return feature


def to_geojson_collection(places: list[GeonPlace]) -> dict[str, Any]:
    """Convert multiple GeonPlace objects to a GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "features": [to_geojson(p) for p in places],
    }


def to_geojson_string(place: GeonPlace | list[GeonPlace], indent: int = 2) -> str:
    """Serialize GEON to a GeoJSON string."""
    if isinstance(place, list):
        return json.dumps(to_geojson_collection(place), indent=indent)
    return json.dumps(to_geojson(place), indent=indent)
