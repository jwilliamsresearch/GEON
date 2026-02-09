"""Fetch a POI or polygon from OpenStreetMap and convert to GEON.

Uses the Overpass API to query OSM data directly.

Requirements:
    pip install requests
    (or: pip install geon[osm])
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import geon
from geon.models import Coordinate, GeonPlace

try:
    import requests
except ImportError:
    print("This example requires the 'requests' package.")
    print("Install with:  pip install requests")
    sys.exit(1)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def overpass_query(query: str) -> dict:
    """Run an Overpass QL query and return the JSON response."""
    resp = requests.get(OVERPASS_URL, params={"data": query}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def osm_element_to_geon(element: dict, tags: dict | None = None) -> GeonPlace:
    """Convert a single OSM element (node/way/relation) to GeonPlace."""
    tags = tags or element.get("tags", {})

    p = GeonPlace()
    p.place = tags.get("name", tags.get("name:en", "Unnamed"))
    p.id = f"osm:{element['type']}/{element['id']}"

    # Infer type from OSM tags
    type_props = {k: v for k, v in tags.items()
                  if k in ("building", "highway", "railway", "leisure",
                           "amenity", "natural", "landuse", "tourism")}
    inferred = geon.from_geojson({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "properties": type_props,
    })
    p.type = inferred.type if inferred.type != "hybrid" else _guess_type(tags)

    # Location
    if element["type"] == "node":
        p.location = Coordinate(lat=element["lat"], lon=element["lon"])
    elif "center" in element:
        p.location = Coordinate(lat=element["center"]["lat"],
                                lon=element["center"]["lon"])
    elif "bounds" in element:
        b = element["bounds"]
        p.location = Coordinate(
            lat=(b["minlat"] + b["maxlat"]) / 2,
            lon=(b["minlon"] + b["maxlon"]) / 2,
        )

    # Boundary from way geometry
    if "geometry" in element:
        p.boundary = [
            Coordinate(lat=pt["lat"], lon=pt["lon"])
            for pt in element["geometry"]
        ]

    # Purpose from amenity / leisure / shop tags
    for key in ("amenity", "leisure", "shop", "tourism", "sport"):
        if key in tags:
            p.purpose.append(f"{key}: {tags[key]}")

    # Source
    p.source = [f"OpenStreetMap ({element['type']}/{element['id']})"]

    # Extra OSM metadata
    for key in ("opening_hours", "website", "phone", "cuisine", "operator"):
        if key in tags:
            p.extra[key] = tags[key]

    return p


def _guess_type(tags: dict) -> str:
    if "amenity" in tags:
        return "building"
    if "leisure" in tags:
        return "public_space"
    if "highway" in tags:
        return "street"
    return "hybrid"


# ── Example 1: Fetch a specific POI by name ──────────────────────────────

print("=== Example 1: Fetch a POI from OSM (Nottingham Castle) ===\n")

query_poi = """
[out:json][timeout:10];
node["name"="Nottingham Castle"]["tourism"](around:5000,52.9481,-1.1560);
out body;
"""

try:
    data = overpass_query(query_poi)
    if data["elements"]:
        el = data["elements"][0]
        place = osm_element_to_geon(el)
        print(geon.generate(place))

        # Validate
        result = geon.validate(place)
        print(f"Valid: {result.valid}")
        for issue in result.issues:
            print(f"  {issue}")
    else:
        print("No results found. Showing fallback example...\n")
        raise requests.ConnectionError("No results")
except Exception as e:
    print(f"(Could not reach Overpass API: {e})")
    print("Showing offline example instead:\n")
    place = GeonPlace(
        place="Nottingham Castle",
        type="landmark",
        id="osm:node/12345",
        location=Coordinate(52.9481, -1.1560),
        purpose=["tourism: castle", "leisure: museum"],
        source=["OpenStreetMap (offline example)"],
    )
    print(geon.generate(place))

# ── Example 2: Fetch a polygon (park) ────────────────────────────────────

print("\n=== Example 2: Fetch a polygon from OSM (Wollaton Park) ===\n")

query_polygon = """
[out:json][timeout:10];
way["name"="Wollaton Park"]["leisure"="park"](around:10000,52.9481,-1.1560);
out body geom;
"""

try:
    data = overpass_query(query_polygon)
    if data["elements"]:
        el = data["elements"][0]
        place = osm_element_to_geon(el)
        print(geon.generate(place))
    else:
        print("No results found. Showing fallback...\n")
        raise requests.ConnectionError("No results")
except Exception as e:
    print(f"(Could not reach Overpass API: {e})")
    print("Showing offline polygon example instead:\n")
    place = GeonPlace(
        place="Wollaton Park",
        type="public_space",
        id="osm:way/67890",
        location=Coordinate(52.9518, -1.2092),
        boundary=[
            Coordinate(52.955, -1.215),
            Coordinate(52.955, -1.203),
            Coordinate(52.948, -1.203),
            Coordinate(52.948, -1.215),
            Coordinate(52.955, -1.215),
        ],
        area="202 hectares",
        purpose=["leisure: park", "tourism: attraction"],
        character=["historic (Elizabethan hall)", "natural (deer park)"],
        source=["OpenStreetMap (offline example)"],
    )
    print(geon.generate(place))

# ── Example 3: Fetch multiple POIs in an area ────────────────────────────

print("\n=== Example 3: All pubs within 500m of Nottingham centre ===\n")

query_pubs = """
[out:json][timeout:10];
node["amenity"="pub"](around:500,52.9548,-1.1581);
out body 5;
"""

try:
    data = overpass_query(query_pubs)
    places = [osm_element_to_geon(el) for el in data["elements"]]
    if places:
        for p in places:
            print(f"  {p.place} @ {p.location}")
        print(f"\nShowing first result as GEON:\n")
        print(geon.generate(places[0]))
    else:
        raise requests.ConnectionError("No results")
except Exception as e:
    print(f"(Could not reach Overpass API: {e})")
    print("Skipping live query example.")
