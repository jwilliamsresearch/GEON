# GEON for JavaScript/TypeScript (`geon-js`)

A universal TypeScript library for **GEON**, running anywhere JavaScript runs (Node.js, Deno, Bun, Browsers).

## Overview

`geon-js` brings spatial reasoning to the web. It is ideal for:
- **Web Applications**: Visualizing and editing GEON data directly in the browser.
- **Serverless**: Lightweight parsing in AWS Lambda / Cloudflare Workers.
- **Node.js**: Backends for spatial APIs.

## Installation

```bash
npm install geon-js
```

*(Note: Package name is a placeholder for local development)*

## TypeScript API

The library exports full type definitions for robust development.

### `const place: GeonPlace = parse(text);`

```typescript
import { parse, GeonPlace } from 'geon-js';

const text = `
PLACE: Shoreditch High St
TYPE: street
`;

const place: GeonPlace = parse(text);
```

### `const text: string = generate(place);`

Generates validated GEON text.

### `const places: GeonPlace[] = fromGeoJSON(featureCollection);`

Converts standard GeoJSON into GEON objects. This is useful for utilizing existing map data libraries like Leaflet or Mapbox GL JS to source data.

## Browser Usage

`geon-js` is ES-module native. You can import it directly in modern build tools (Vite, Webpack) or use it via `<script type="module">` if bundled.

```javascript
import { parse } from './dist/index.js';

fetch('data.geon')
  .then(res => res.text())
  .then(text => {
     const place = parse(text);
     console.log("Loaded Place:", place.place);
  });
```

## Data Model

The `GeonPlace` class acts as the central data structure.

```typescript
class GeonPlace {
    place: string;
    type: string;
    location: Coordinate | null;
    boundary: Coordinate[];
    
    // Semantic
    purpose: string[];
    experience: Record<string, string>;
    
    // Relations
    contains: GeonPlace[];
    // ...
}
```

## Running Tests & Examples

This project uses `ts-node` for running examples directly from source.

```bash
# Run the OSM fetcher example
npx ts-node examples/03_from_osm.ts

# Run the unit test suite
npm test
```
