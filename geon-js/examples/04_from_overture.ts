import { GeonPlace, generate } from '../src';

function overtureToGeon(feature: any): GeonPlace {
    const p = new GeonPlace();
    const props = feature.properties || {};
    const geom = feature.geometry || {};

    // Name
    if (props.names && props.names.primary) {
        p.place = props.names.primary;
    } else {
        p.place = props.name || "Unnamed";
    }

    // ID
    p.id = props.id || feature.id;

    // Categories
    if (props.categories && props.categories.main) {
        const cat = props.categories.main;
        if (cat.includes("restaurant") || cat.includes("shop")) p.type = "building";
        else if (cat.includes("park")) p.type = "public_space";
        else if (cat.includes("castle")) p.type = "landmark";
        else p.type = "hybrid";
    }

    // Location
    if (geom.type === "Point" && geom.coordinates) {
        p.location = { lat: geom.coordinates[1], lon: geom.coordinates[0] };
    }

    if (props.confidence) {
        p.confidence["overall"] = String(props.confidence);
    }

    if (props.sources) {
        for (const s of props.sources) {
            if (s.dataset) p.source.push(`Overture Maps (${s.dataset})`);
        }
    }

    return p;
}

console.log("=== Example 1: Overture Maps feature -> GEON ===\n");

const overtureFeature = {
    "type": "Feature",
    "id": "08f194ad-3241-0744-0200-54a1a98e6d95",
    "geometry": {
        "type": "Point",
        "coordinates": [-1.1490, 52.9534],
    },
    "properties": {
        "id": "08f194ad-3241-0744-0200-54a1a98e6d95",
        "names": {
            "primary": "Ye Olde Trip to Jerusalem",
        },
        "categories": {
            "main": "bar",
            "alternate": ["pub", "historic_pub", "tourism"],
        },
        "confidence": 0.92,
        "sources": [
            { "dataset": "meta" },
            { "dataset": "microsoft" },
        ],
        "addresses": [
            { "freeform": "1 Brewhouse Yard, Nottingham NG1 6AD" },
        ],
        "websites": ["https://www.triptojerusalem.com"],
    },
};

const p = overtureToGeon(overtureFeature);
p.character = ["historic", "atmospheric"];
console.log(generate(p));
