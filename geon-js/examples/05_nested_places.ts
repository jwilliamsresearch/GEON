import { GeonPlace, generate, parse } from '../src';

const grandCentral = new GeonPlace();
grandCentral.place = "Grand Central Birmingham";
grandCentral.type = "building";
grandCentral.location = { lat: 52.4774, lon: -1.8984 };
grandCentral.area = "75000 sqm";
grandCentral.purpose = ["retail", "transport"];
grandCentral.contains = [
    (() => {
        const c = new GeonPlace();
        c.place = "John Lewis";
        c.type = "building";
        c.purpose = ["retail"];
        return c;
    })(),
    (() => {
        const c = new GeonPlace();
        c.place = "Grand Central Shopping Centre";
        c.type = "building";
        return c;
    })()
];

const text = generate(grandCentral);
console.log("=== Nested GEON Document ===");
console.log(text);

const parsed = parse(text);
console.log(`=== Parsed: ${parsed.place} ===`);
console.log(`Contains ${parsed.contains.length} sub-places:`);
for (const child of parsed.contains) {
    console.log(`  - ${child.place} (${child.type})`);
}
