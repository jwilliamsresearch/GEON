"""Parse the full Appendix A example from the GEON spec.

Demonstrates that the parser handles all field types including
extended domain fields (BUILT_FORM, INFRASTRUCTURE, DEMOGRAPHICS, ECONOMY).

No external dependencies required.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import geon

APPENDIX_A = """\
PLACE: Birmingham Bullring Markets
TYPE: public_space
ID: osgb:1000000347112034
LOCATION: 52.4777, -1.8933
BOUNDARY:
  - 52.4780, -1.8940
  - 52.4780, -1.8926
  - 52.4774, -1.8926
  - 52.4774, -1.8940
  - 52.4780, -1.8940
AREA: 4200 sqm
ELEVATION: 142m above sea level

PURPOSE:
  - retail (fresh food, flowers, clothing)
  - social gathering
  - cultural heritage (market tradition since 1166)
  - circulation (pedestrian link)

EXPERIENCE:
  openness: medium
  enclosure: medium-high (surrounding buildings)
  activity_density: high (weekdays), very_high (weekends)
  noise_level: loud
  visual_complexity: very_high (stalls, signage, products)
  sense_of_safety: high (daytime), moderate (evening)
  social_diversity: very_high

CHARACTER:
  - vibrant (energetic street market atmosphere)
  - diverse (multicultural vendors and shoppers)
  - authentic (working market, not tourist recreation)
  - gritty (worn surfaces, informal trade)

ADJACENCIES:
  - Bullring Shopping Centre (immediate south)
  - St Martin's Church (100m west)
  - Moor Street Station (200m east)
  - Smithfield Market site (300m north)

CONNECTIVITY:
  pedestrian_entries: 4 (north, south, east, west)
  vehicular_access: service only (05:00-11:00)
  cycling: Rea Valley Route (via Digbeth)

CONTAINS:
  - PLACE: Outdoor Market
    TYPE: public_space
    LOCATION: 52.4777, -1.8935
    PURPOSE: retail (fresh produce, flowers)
    TEMPORAL:
      trading_days: Tuesday, Thursday, Friday, Saturday
      trading_hours: 09:00-17:00

  - PLACE: Rag Market
    TYPE: building
    LOCATION: 52.4776, -1.8931
    PURPOSE: retail (clothing, textiles, household)
    TEMPORAL:
      trading_days: Tuesday, Thursday, Friday, Saturday
      trading_hours: 09:00-17:00

PART_OF: Digbeth and Eastside

VIEWSHEDS:
  - St Martin's Church spire (prominent, 100m west)
  - Rotunda (visible, 200m southwest)
  - Selfridges building (immediate south, iconic facade)

TEMPORAL:
  weekday_footfall: 5000-8000 people/hour (Thursday peak)
  weekend_footfall: 8000-12000 people/hour (Saturday peak)
  seasonal_variation: +30% December (Christmas), -20% January
  event_schedule: none (regular trading only)

BUILT_FORM:
  market_hall_height: 2 stories
  stall_configuration: modular (2m x 2m typical)
  canopy: metal frame with fabric (outdoor market)
  materials: brick (hall), steel and fabric (outdoor), asphalt (ground)
  condition: fair (worn, functional, some weathering)

INFRASTRUCTURE:
  utilities: electricity (stalls), water (limited), drainage
  waste_management: commercial collection (daily)
  digital: mobile coverage (good), limited public WiFi

DEMOGRAPHICS:
  vendor_count: ~120 (variable)
  visitor_demographics: diverse (age, ethnicity, socioeconomic)
  catchment: Birmingham city region + tourist visitors

ECONOMY:
  stall_rents: 50-150 per day (estimated, varies by location)
  employment: ~200 traders + support staff

SOURCE:
  - Ordnance Survey MasterMap Topography Layer (2024-11)
  - Birmingham City Council market data (2024)
  - OpenStreetMap (2025-01)
  - Field observation (2025-01-18, Saturday 11:00-13:00)
  - Historical records (Birmingham Archives)

CONFIDENCE:
  geometry: high (OS survey)
  footfall: medium (council estimates, not direct measurement)
  experience_qualities: medium (single observation, winter)
  economic_data: low (estimated from partial sources)

UPDATED: 2025-01-20T09:00:00Z
"""

# ── Parse ─────────────────────────────────────────────────────────────────

place = geon.parse(APPENDIX_A)

print("=== Parsed Appendix A ===")
print(f"Place:       {place.place}")
print(f"Type:        {place.type}")
print(f"ID:          {place.id}")
print(f"Location:    {place.location}")
print(f"Boundary:    {len(place.boundary)} points")
print(f"Area:        {place.area}")
print(f"Elevation:   {place.elevation}")
print(f"Purposes:    {len(place.purpose)} items")
print(f"Experience:  {len(place.experience)} qualities")
print(f"Character:   {len(place.character)} traits")
print(f"Adjacencies: {len(place.adjacencies)} neighbours")
print(f"Contains:    {len(place.contains)} sub-places")
for child in place.contains:
    print(f"  - {child.place} ({child.type})")
print(f"Part of:     {place.part_of}")
print(f"Viewsheds:   {len(place.viewsheds)} views")
print(f"Temporal:    {len(place.temporal)} patterns")
print(f"Built form:  {len(place.built_form)} attributes")
print(f"Sources:     {len(place.source)} sources")
print(f"Confidence:  {len(place.confidence)} fields")
print(f"Updated:     {place.updated}")
print()

# ── Validate ──────────────────────────────────────────────────────────────

result = geon.validate(place)
print(f"Valid: {result.valid}")
print(f"Errors:   {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")
for issue in result.issues:
    print(f"  {issue}")
print()

# ── Convert to GeoJSON ───────────────────────────────────────────────────

geojson_str = geon.to_geojson_string(place, indent=2)
print("=== GeoJSON output (truncated) ===")
lines = geojson_str.split("\n")
for line in lines[:30]:
    print(line)
if len(lines) > 30:
    print(f"  ... ({len(lines) - 30} more lines)")
print()

# ── Re-generate GEON text ────────────────────────────────────────────────

regenerated = geon.generate(place)
print("=== Re-generated GEON (first 40 lines) ===")
for line in regenerated.split("\n")[:40]:
    print(line)
