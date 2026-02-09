import { parse, generate } from '../src';

const appendixA = `
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

EXPERIENCE:
  openness: medium
  noise_level: loud

CHARACTER:
  - vibrant
  - diverse

CONTAINS:
  - PLACE: Outdoor Market
    TYPE: public_space
    LOCATION: 52.4777, -1.8935

  - PLACE: Rag Market
    TYPE: building
    LOCATION: 52.4776, -1.8931

VIEWSHEDS:
  - St Martin's Church spire (prominent, 100m west)
  - Rotunda (visible, 200m southwest)

TEMPORAL:
  weekday_footfall: 5000-8000 people/hour

BUILT_FORM:
  market_hall_height: 2 stories
  stall_configuration: modular

SOURCE:
  - Ordnance Survey MasterMap Topography Layer (2024-11)
`;

const place = parse(appendixA);
console.log("=== Parsed Appendix A ===");
console.log(`Place: ${place.place}`);
console.log(`Type: ${place.type}`);
console.log(`Boundary: ${place.boundary.length} points`);
console.log(`Contains: ${place.contains.length} sub-places`);
for (const child of place.contains) {
    console.log(`  - ${child.place}`);
}

const regenerated = generate(place);
console.log("\n=== Re-generated GEON (first 40 lines) ===");
console.log(regenerated.split('\n').slice(0, 40).join('\n'));
