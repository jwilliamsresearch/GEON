import { GeonPlace, Coordinate, generate, parse, fromGeoJSON } from '../src';

// --------------------
// 1. Programmatic creation
// --------------------

const place = new GeonPlace();
place.place = "Test Place"; // Basic string
place.type = "public_space";
place.location = { lat: 51.5074, lon: -0.1278 };
place.purpose = ["gathering", "recreation"];
place.experience = {
    "openness": "high",
    "noise": "low"
};

console.log("=== Created Object ===");
console.log(place);

// --------------------
// 2. Generate
// --------------------

const text = generate(place);
console.log("\n=== Generated GEON ===");
console.log(text);

// --------------------
// 3. Parse
// --------------------

const parsed = parse(text);
console.log("=== Parsed Back ===");
console.log(`Place: ${parsed.place}`);
console.log(`Location: ${parsed.location?.lat}, ${parsed.location?.lon}`);
console.log(`Purpose: ${parsed.purpose.join(", ")}`);
