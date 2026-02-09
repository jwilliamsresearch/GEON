import { GeonPlace, Coordinate, Extent } from './models';

// ---------------------------------------------------------------------------
// Low-level helpers
// ---------------------------------------------------------------------------

const COORD_RE = /^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/;

function indentLevel(line: string): number {
    return line.length - line.trimStart().length;
}

function parseCoordinate(text: string): Coordinate | null {
    const m = COORD_RE.exec(text);
    if (m) {
        return { lat: parseFloat(m[1]), lon: parseFloat(m[2]) };
    }
    return null;
}

function splitKeyValue(line: string): [string, string] | null {
    const stripped = line.trim();
    const idx = stripped.indexOf(':');
    if (idx === -1) return null;
    const key = stripped.substring(0, idx).trim();
    const value = stripped.substring(idx + 1).trim();
    return [key, value];
}

// ---------------------------------------------------------------------------
// Block builder
// ---------------------------------------------------------------------------

interface Line {
    indent: number;
    content: string;
}

function tokenizeLines(text: string): Line[] {
    return text.split('\n')
        .filter(line => line.trim().length > 0)
        .map(line => ({
            indent: indentLevel(line),
            content: line.trim()
        }));
}

function parseBlock(lines: Line[], start: number, baseIndent: number): [any, number] {
    const result: any = {};
    let i = start;

    while (i < lines.length) {
        const line = lines[i];

        if (line.indent < baseIndent) {
            break;
        }

        if (line.indent > baseIndent) {
            i++;
            continue;
        }

        const kv = splitKeyValue(line.content);
        if (kv) {
            const [key, value] = kv;
            if (value) {
                result[key] = value;
                i++;
            } else {
                const [children, nextI] = collectChildren(lines, i + 1, baseIndent + 2);
                result[key] = children;
                i = nextI;
            }
        } else {
            i++;
        }
    }

    return [result, i];
}

function collectChildren(lines: Line[], start: number, childIndent: number): [any, number] {
    if (start >= lines.length) return [[], start];

    const firstLine = lines[start];
    if (firstLine.indent < childIndent) return [[], start];

    const isList = firstLine.content.startsWith('- ');

    if (isList) {
        const items: any[] = [];
        let i = start;

        while (i < lines.length) {
            const line = lines[i];
            if (line.indent < childIndent) break;

            if (line.indent === childIndent && line.content.startsWith('- ')) {
                const itemText = line.content.substring(2).trim();

                const kv = splitKeyValue(itemText);
                if (kv && kv[0] === 'PLACE') {
                    let j = i + 1;
                    while (j < lines.length && lines[j].indent > childIndent) {
                        j++;
                    }
                    const fieldIndent = (j > i + 1) ? lines[i + 1].indent : childIndent + 2;
                    const [subBlock, _] = parseBlock(lines, i + 1, fieldIndent);

                    if (kv) subBlock[kv[0]] = kv[1];

                    items.push(subBlock);
                    i = j;
                    continue;
                }

                let j = i + 1;
                while (j < lines.length && lines[j].indent > childIndent) {
                    j++;
                }

                if (j > i + 1) {
                    const fieldIndent = lines[i + 1].indent;
                    const [subBlock, _] = parseBlock(lines, i + 1, fieldIndent);
                    if (kv) {
                        subBlock[kv[0]] = kv[1];
                    } else {
                        subBlock["_value"] = itemText;
                    }
                    items.push(subBlock);
                    i = j;
                } else {
                    items.push(itemText);
                    i++;
                }
            } else {
                i++;
            }
        }
        return [items, i];
    } else {
        return parseBlock(lines, start, childIndent);
    }
}

// ---------------------------------------------------------------------------
// Conversion to GeonPlace
// ---------------------------------------------------------------------------

function rawToPlace(raw: any): GeonPlace {
    const p = new GeonPlace();

    if (raw["PLACE"]) p.place = raw["PLACE"];
    if (raw["TYPE"]) p.type = raw["TYPE"];
    if (raw["ID"]) p.id = raw["ID"];

    if (raw["LOCATION"]) p.location = parseCoordinate(raw["LOCATION"]);

    if (raw["BOUNDARY"] && Array.isArray(raw["BOUNDARY"])) {
        for (const item of raw["BOUNDARY"]) {
            const coord = parseCoordinate(typeof item === 'string' ? item : String(item));
            if (coord) p.boundary.push(coord);
        }
    }

    if (raw["EXTENT"]) {
        const parts = String(raw["EXTENT"]).split(',').map(s => s.trim());
        if (parts.length === 4) {
            p.extent = {
                north: parseFloat(parts[0]),
                south: parseFloat(parts[1]),
                east: parseFloat(parts[2]),
                west: parseFloat(parts[3])
            };
        }
    }

    if (raw["ELEVATION"]) p.elevation = raw["ELEVATION"];
    if (raw["AREA"]) p.area = raw["AREA"];

    const toStringList = (val: any): string[] => {
        if (Array.isArray(val)) return val.map(String);
        if (typeof val === 'string') return [val];
        return [];
    };

    const toStringMap = (val: any): Record<string, string> => {
        if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
            const res: Record<string, string> = {};
            for (const k in val) {
                res[k] = String(val[k]);
            }
            return res;
        }
        return {};
    };

    p.purpose = toStringList(raw["PURPOSE"]);
    p.experience = toStringMap(raw["EXPERIENCE"]);
    p.character = toStringList(raw["CHARACTER"]);
    p.adjacencies = toStringList(raw["ADJACENCIES"]);
    p.connectivity = toStringMap(raw["CONNECTIVITY"]);

    if (raw["CONTAINS"] && Array.isArray(raw["CONTAINS"])) {
        for (const item of raw["CONTAINS"]) {
            if (typeof item === 'object') {
                p.contains.push(rawToPlace(item));
            } else if (typeof item === 'string') {
                const child = new GeonPlace();
                child.place = item;
                p.contains.push(child);
            }
        }
    }

    if (raw["PART_OF"]) p.part_of = raw["PART_OF"];

    if (raw["VIEWSHEDS"]) p.viewsheds = raw["VIEWSHEDS"];

    p.temporal = raw["TEMPORAL"] || {};
    p.lifespan = toStringMap(raw["LIFESPAN"]);
    p.source = toStringList(raw["SOURCE"]);
    p.confidence = toStringMap(raw["CONFIDENCE"]);
    p.updated = raw["UPDATED"] || null;

    p.built_form = raw["BUILT_FORM"] || {};
    p.ecology = raw["ECOLOGY"] || {};
    p.infrastructure = raw["INFRASTRUCTURE"] || {};
    p.demographics = raw["DEMOGRAPHICS"] || {};
    p.economy = raw["ECONOMY"] || {};
    p.visual = raw["VISUAL"] || {};
    p.vertical_profile = raw["VERTICAL_PROFILE"] || {};

    if (Array.isArray(raw["HISTORY"])) {
        p.history = raw["HISTORY"];
    }

    const known = new Set([
        "PLACE", "TYPE", "ID", "LOCATION", "BOUNDARY", "EXTENT", "ELEVATION",
        "AREA", "PURPOSE", "EXPERIENCE", "CHARACTER", "ADJACENCIES",
        "CONNECTIVITY", "CONTAINS", "PART_OF", "VIEWSHEDS", "TEMPORAL",
        "LIFESPAN", "SOURCE", "CONFIDENCE", "UPDATED", "BUILT_FORM",
        "ECOLOGY", "INFRASTRUCTURE", "DEMOGRAPHICS", "ECONOMY", "VISUAL",
        "HISTORY", "VERTICAL_PROFILE"
    ]);

    for (const k in raw) {
        if (!known.has(k)) {
            p.extra[k] = raw[k];
        }
    }

    return p;
}

export function parse(text: string): GeonPlace {
    const lines = tokenizeLines(text);
    if (lines.length === 0) return new GeonPlace();
    const [raw, _] = parseBlock(lines, 0, 0);
    return rawToPlace(raw);
}
