import { GeonPlace, Coordinate } from './models';

// ---------------------------------------------------------------------------
// GeoJSON -> GEON
// ---------------------------------------------------------------------------

const TYPE_MAPPING: Record<string, string> = {
    "park": "public_space",
    "garden": "public_space",
    "playground": "public_space",
    "plaza": "public_space",
    "square": "public_space",
    "marketplace": "public_space",
    "yes": "building",
    "house": "building",
    "apartments": "building",
    "commercial": "building",
    "retail": "building",
    "office": "building",
    "school": "building",
    "hospital": "building",
    "railway_station": "transport_hub",
    "station": "transport_hub",
    "bus_station": "transport_hub",
    "airport": "transport_hub",
    "monument": "landmark",
    "memorial": "landmark",
    "church": "building",
    "cathedral": "building"
};

function inferType(props: any): string {
    if (props["geon_type"]) return String(props["geon_type"]);

    const keys = ["type", "building", "highway", "railway", "leisure", "amenity", "natural", "landuse"];
    for (const k of keys) {
        if (props[k]) {
            const val = String(props[k]);
            if (TYPE_MAPPING[val]) return TYPE_MAPPING[val];
        }
    }
    return "hybrid";
}

function inferName(props: any): string {
    const keys = ["name", "name:en", "official_name", "title", "label"];
    for (const k of keys) {
        if (props[k]) return String(props[k]);
    }
    return "Unnamed";
}

function extractCentroid(geom: any): Coordinate | null {
    if (!geom || !geom.type) return null;
    const coords = geom.coordinates;
    if (!coords) return null;

    if (geom.type === "Point") {
        return { lat: coords[1], lon: coords[0] };
    }
    if (geom.type === "Polygon") {
        // Average first ring
        const ring = coords[0];
        if (Array.isArray(ring) && ring.length > 0) {
            let latSum = 0, lonSum = 0;
            for (const pt of ring) {
                lonSum += pt[0];
                latSum += pt[1];
            }
            return { lat: latSum / ring.length, lon: lonSum / ring.length };
        }
    }
    return null;
}

function featureToGeon(feature: any): GeonPlace {
    const props = feature.properties || {};
    const geom = feature.geometry || {};

    const p = new GeonPlace();
    p.place = inferName(props);
    p.type = inferType(props);
    p.location = extractCentroid(geom);

    // Boundary from Polygon
    if (geom.type === "Polygon" && geom.coordinates && geom.coordinates.length > 0) {
        p.boundary = geom.coordinates[0].map((pt: number[]) => ({
            lat: pt[1],
            lon: pt[0]
        }));
    }

    // ID
    const fid = feature.id || props.id || props["@id"];
    if (fid) p.id = String(fid);

    // Purpose inference simplified
    if (props.amenity) p.purpose.push(String(props.amenity));
    if (props.leisure) p.purpose.push(String(props.leisure));
    if (props.shop) p.purpose.push(`retail (${props.shop})`);

    // Experience
    if (props.experience && typeof props.experience === 'object') {
        for (const k in props.experience) {
            p.experience[k] = String(props.experience[k]);
        }
    }

    p.source.push("GeoJSON conversion");

    return p;
}

export function fromGeoJSON(json: any): GeonPlace[] {
    if (json.type === "FeatureCollection" && Array.isArray(json.features)) {
        return json.features.map(featureToGeon);
    }
    if (json.type === "Feature") {
        return [featureToGeon(json)];
    }
    return [];
}
