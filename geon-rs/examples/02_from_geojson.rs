use geon_rs::{GeonPlace, generate, from_geojson};
use serde_json::json;

fn main() {
    // 1. Point feature
    let point_geojson = json!({
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
    });

    // from_geojson returns a Vec
    let places = from_geojson(point_geojson.clone());
    let place = &places[0];
    println!("=== Point Feature -> GEON ===");
    println!("{}", generate(place));

    // 2. Polygon feature
    let polygon_geojson = json!({
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
    });

    let places2 = from_geojson(polygon_geojson.clone());
    let place2 = &places2[0];
    println!("=== Polygon Feature -> GEON ===");
    println!("{}", generate(place2));

    // 3. FeatureCollection
    let collection = json!({
        "type": "FeatureCollection",
        "features": [point_geojson, polygon_geojson],
    });

    let places_col = from_geojson(collection);
    println!("=== FeatureCollection -> {} GEON places ===", places_col.len());
    for p in &places_col {
        println!("  - {} ({})", p.place, p.type_);
    }
    println!();
}
