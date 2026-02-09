import { GeonPlace, generate, parse } from '../src';
import * as fs from 'fs';
import * as path from 'path';

// 1. Create a sample .geon object
const place = new GeonPlace();
place.place = "Victoria Park, Nottingham";
place.type = "public_space";
place.location = { lat: 52.9403, lon: -1.1340 };
place.source = ["OpenStreetMap (2025-01)"];

// Write to a temp file
const filename = path.join(__dirname, "example_07_temp.geon");
const text = generate(place);

fs.writeFileSync(filename, text, 'utf8');
console.log(`Wrote GEON file: ${filename}`);
console.log(`Size: ${text.length} bytes\n`);

// 2. Read it back
const loadedText = fs.readFileSync(filename, 'utf8');
const loaded = parse(loadedText);

console.log(`Loaded: ${loaded.place}`);
console.log(`Type:   ${loaded.type}`);
console.log();

// 3. Modify and save
loaded.temporal["summer_events"] = "concerts every Friday July-August";
loaded.adjacencies.push("Sneinton Market (500m north)");

const updatedText = generate(loaded);
const filename2 = path.join(__dirname, "example_07_temp_updated.geon");
fs.writeFileSync(filename2, updatedText, 'utf8');

console.log(`Updated GEON file: ${filename2}`);
console.log(`Size: ${updatedText.length} bytes\n`);
console.log("=== Updated content ===");
console.log(updatedText);

// Clean up
try {
    fs.unlinkSync(filename);
    fs.unlinkSync(filename2);
} catch (e) {
    // ignore
}
