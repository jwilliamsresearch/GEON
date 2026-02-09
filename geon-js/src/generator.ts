import { GeonPlace } from './models';

const INDENT = "  ";

function writeIndent(depth: number): string {
    return INDENT.repeat(depth);
}

function writeLine(key: string, value: string, depth: number): string {
    return `${writeIndent(depth)}${key}: ${value}\n`;
}

function writeSection(key: string, depth: number): string {
    return `${writeIndent(depth)}${key}:\n`;
}

function writeList(items: string[], depth: number): string {
    let buf = "";
    for (const item of items) {
        buf += `${writeIndent(depth)}- ${item}\n`;
    }
    return buf;
}

function writeDict(map: Record<string, any>, depth: number): string {
    let buf = "";
    // Sort keys for deterministic output
    const keys = Object.keys(map).sort();
    for (const key of keys) {
        const val = map[key];
        if (typeof val === 'object' && val !== null) {
            // Recursive dict or list?
            // Basic GEON dicts are string: string.
            // But extended fields might have structure.
            // For now, assume string or simple object.
            buf += `${writeIndent(depth)}${key}:\n`;
            // Recurse?
            // if generic object, likely need recursive writeDict
            // But for main fields it's string: string
            if (!Array.isArray(val)) {
                buf += writeDict(val, depth + 1);
            }
        } else {
            buf += `${writeIndent(depth)}${key}: ${val}\n`;
        }
    }
    return buf;
}

function generateNested(place: GeonPlace, depth: number): string {
    let buf = `${writeIndent(depth)}- PLACE: ${place.place}\n`;
    const inner = depth + 2;

    if (place.type) buf += writeLine("TYPE", place.type, inner);
    if (place.location) buf += writeLine("LOCATION", `${place.location.lat}, ${place.location.lon}`, inner);
    if (place.area) buf += writeLine("AREA", place.area, inner);

    if (place.purpose.length > 0) {
        if (place.purpose.length === 1) {
            buf += writeLine("PURPOSE", place.purpose[0], inner);
        } else {
            buf += writeSection("PURPOSE", inner);
            buf += writeList(place.purpose, inner + 1);
        }
    }

    if (Object.keys(place.temporal).length > 0) {
        buf += writeSection("TEMPORAL", inner);
        buf += writeDict(place.temporal, inner + 1);
    }

    return buf;
}

export function generate(place: GeonPlace): string {
    let buf = "";

    // Identity
    buf += writeLine("PLACE", place.place, 0);
    if (place.type) buf += writeLine("TYPE", place.type, 0);
    if (place.id) buf += writeLine("ID", place.id, 0);

    // Geometry
    if (place.location) {
        buf += writeLine("LOCATION", `${place.location.lat}, ${place.location.lon}`, 0);
    }

    if (place.boundary.length > 0) {
        buf += writeSection("BOUNDARY", 0);
        const items = place.boundary.map(c => `${c.lat}, ${c.lon}`);
        buf += writeList(items, 1);
    }

    if (place.extent) {
        const e = place.extent;
        buf += writeLine("EXTENT", `${e.north}, ${e.south}, ${e.east}, ${e.west}`, 0);
    }
    if (place.elevation) buf += writeLine("ELEVATION", place.elevation, 0);
    if (place.area) buf += writeLine("AREA", place.area, 0);

    // Semantic
    if (place.purpose.length > 0) {
        if (place.purpose.length === 1) {
            buf += writeLine("PURPOSE", place.purpose[0], 0);
        } else {
            buf += writeSection("PURPOSE", 0);
            buf += writeList(place.purpose, 1);
        }
    }

    if (Object.keys(place.experience).length > 0) {
        buf += writeSection("EXPERIENCE", 0);
        buf += writeDict(place.experience, 1);
    }

    if (place.character.length > 0) {
        buf += writeSection("CHARACTER", 0);
        buf += writeList(place.character, 1);
    }

    // Relational
    if (place.adjacencies.length > 0) {
        buf += writeSection("ADJACENCIES", 0);
        buf += writeList(place.adjacencies, 1);
    }

    if (Object.keys(place.connectivity).length > 0) {
        buf += writeSection("CONNECTIVITY", 0);
        buf += writeDict(place.connectivity, 1);
    }

    if (place.contains.length > 0) {
        buf += writeSection("CONTAINS", 0);
        for (const child of place.contains) {
            buf += generateNested(child, 1);
            buf += "\n";
        }
    }

    if (place.part_of) buf += writeLine("PART_OF", place.part_of, 0);

    if (Array.isArray(place.viewsheds)) {
        if (place.viewsheds.length > 0) {
            buf += writeSection("VIEWSHEDS", 0);
            buf += writeList(place.viewsheds as string[], 1);
        }
    } else if (Object.keys(place.viewsheds).length > 0) {
        buf += writeSection("VIEWSHEDS", 0);
        buf += writeDict(place.viewsheds, 1);
    }

    // Temporal
    if (Object.keys(place.temporal).length > 0) {
        buf += writeSection("TEMPORAL", 0);
        buf += writeDict(place.temporal, 1);
    }
    if (Object.keys(place.lifespan).length > 0) {
        buf += writeSection("LIFESPAN", 0);
        buf += writeDict(place.lifespan, 1);
    }

    // Provenance
    if (place.source.length > 0) {
        buf += writeSection("SOURCE", 0);
        buf += writeList(place.source, 1);
    }
    if (Object.keys(place.confidence).length > 0) {
        buf += writeSection("CONFIDENCE", 0);
        buf += writeDict(place.confidence, 1);
    }
    if (place.updated) buf += writeLine("UPDATED", place.updated, 0);

    // Extended
    const extendedFields = [
        ["BUILT_FORM", place.built_form],
        ["ECOLOGY", place.ecology],
        ["INFRASTRUCTURE", place.infrastructure],
        ["DEMOGRAPHICS", place.demographics],
        ["ECONOMY", place.economy],
        ["VISUAL", place.visual],
        ["VERTICAL_PROFILE", place.vertical_profile]
    ] as const;

    for (const [key, map] of extendedFields) {
        if (Object.keys(map).length > 0) {
            buf += writeSection(key, 0);
            buf += writeDict(map, 1);
        }
    }

    if (place.history.length > 0) {
        buf += writeSection("HISTORY", 0);
        for (const h of place.history) {
            buf += writeDict(h, 1); // Simplification, history list of dicts
        }
    }

    // Extra
    for (const key of Object.keys(place.extra).sort()) {
        const val = place.extra[key];
        if (typeof val === 'object') {
            if (Array.isArray(val)) {
                buf += writeSection(key, 0);
                buf += writeList(val.map(String), 1);
            } else {
                buf += writeSection(key, 0);
                buf += writeDict(val, 1);
            }
        } else {
            buf += writeLine(key, String(val), 0);
        }
    }

    return buf;
}
