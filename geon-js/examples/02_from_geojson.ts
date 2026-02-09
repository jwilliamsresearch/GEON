import { GeonPlace, generate, fromGeoJSON } from '../src';

const pointGeoJSON = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [-1.8984, 52.4774],
    },
    "properties": {
        "name": "Birmingham New Street Station",
        "railway": "station",
        "operator": "Network Rail",
        "amenity": "rail transport",
    },
};

const places = fromGeoJSON(pointGeoJSON);
console.log("=== Point Feature -> GEON ===");
console.log(generate(places[0]));

const polygonGeoJSON = {
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [-1.8940, 52.4780],
            [-1.8926, 52.4780],
            [-1.8926, 52.4774],
            [-1.8940, 52.4774],
            [-1.8940, 52.4780],
        ]],
    },
    "properties": {
        "name": "Birmingham Bullring Markets",
        "leisure": "marketplace",
        "shop": "general",
        "experience": {
            "openness": "medium",
            "activity_density": "high",
            "noise_level": "loud",
        },
    },
};

const places2 = fromGeoJSON(polygonGeoJSON);
console.log("=== Polygon Feature -> GEON ===");
console.log(generate(places2[0]));

const collection = {
    "type": "FeatureCollection",
    "features": [pointGeoJSON, polygonGeoJSON],
};

const placesCol = fromGeoJSON(collection);
console.log(`=== FeatureCollection -> ${placesCol.length} GEON places ===`);
for (const p of placesCol) {
    console.log(`  - ${p.place} (${p.type})`);
}
