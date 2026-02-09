import { GeonPlace, generate } from '../src';

// Simple polyfill check
if (!globalThis.fetch) {
    console.error("This example requires Node.js 18+ with native fetch support.");
    process.exit(1);
}

const OVERPASS_URL = "https://overpass-api.de/api/interpreter";

async function overpassQuery(query: string): Promise<any> {
    const params = new URLSearchParams();
    params.append("data", query);
    const resp = await fetch(`${OVERPASS_URL}?${params.toString()}`);
    if (!resp.ok) {
        throw new Error(`HTTP Error: ${resp.status}`);
    }
    return await resp.json();
}

function osmToGeon(element: any): GeonPlace {
    const p = new GeonPlace();
    const tags = element.tags || {};

    // Name
    p.place = tags.name || tags["name:en"] || "Unnamed";

    // ID
    p.id = `osm:${element.type}/${element.id}`;

    // Type
    p.type = "hybrid";
    if (tags.amenity) p.type = "building";
    else if (tags.leisure) p.type = "public_space";
    else if (tags.highway) p.type = "street";

    // Location
    if (element.type === "node") {
        p.location = { lat: element.lat, lon: element.lon };
    } else if (element.center) {
        p.location = { lat: element.center.lat, lon: element.center.lon };
    } else if (element.bounds) {
        p.location = {
            lat: (element.bounds.minlat + element.bounds.maxlat) / 2,
            lon: (element.bounds.minlon + element.bounds.maxlon) / 2
        };
    }

    // Boundary
    if (element.geometry) {
        p.boundary = element.geometry.map((pt: any) => ({ lat: pt.lat, lon: pt.lon }));
    }

    // Purpose etc
    ["amenity", "leisure", "shop", "tourism", "sport"].forEach(k => {
        if (tags[k]) p.purpose.push(`${k}: ${tags[k]}`);
    });

    p.source.push(`OpenStreetMap (${element.type}/${element.id})`);

    ["opening_hours", "website", "phone", "cuisine", "operator"].forEach(k => {
        if (tags[k]) p.extra[k] = tags[k];
    });

    return p;
}

async function main() {
    console.log("=== Example 1: Fetch a POI from OSM (Nottingham Castle) ===\n");
    const queryPoi = `
[out:json][timeout:10];
node["name"="Nottingham Castle"]["tourism"](around:5000,52.9481,-1.1560);
out body;
`;

    try {
        const data = await overpassQuery(queryPoi);
        if (data.elements && data.elements.length > 0) {
            const p = osmToGeon(data.elements[0]);
            console.log(generate(p));
        } else {
            console.log("No results.");
        }
    } catch (err) {
        console.error("Error:", err);
    }

    console.log("\n=== Example 2: Fetch a polygon from OSM (Wollaton Park) ===\n");
    const queryPoly = `
[out:json][timeout:10];
way["name"="Wollaton Park"]["leisure"="park"](around:10000,52.9481,-1.1560);
out body geom;
`;

    try {
        const data = await overpassQuery(queryPoly);
        if (data.elements && data.elements.length > 0) {
            const p = osmToGeon(data.elements[0]);
            console.log(generate(p));
        } else {
            console.log("No results.");
        }
    } catch (err) {
        console.error("Error:", err);
    }
}

main();
