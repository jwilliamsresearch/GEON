use geon_rs::{GeonPlace, Coordinate, generate};
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;

const OVERPASS_URL: &str = "https://overpass-api.de/api/interpreter";

async fn overpass_query(query: &str) -> Result<Value, Box<dyn Error>> {
    let client = reqwest::Client::new();
    let params = [("data", query)];
    let resp = client.get(OVERPASS_URL)
        .query(&params)
        .send()
        .await?
        .json::<Value>()
        .await?;
    Ok(resp)
}

fn osm_element_to_geon(element: &Value) -> GeonPlace {
    let mut p = GeonPlace::default();
    let tags = element.get("tags").and_then(|t| t.as_object());
    
    // Name
    if let Some(tags) = tags {
        if let Some(name) = tags.get("name").and_then(|v| v.as_str()) {
            p.place = name.to_string();
        } else if let Some(name_en) = tags.get("name:en").and_then(|v| v.as_str()) {
            p.place = name_en.to_string();
        } else {
            p.place = "Unnamed".to_string();
        }
    } else {
        p.place = "Unnamed".to_string();
    }
    
    // ID
    let type_ = element.get("type").and_then(|v| v.as_str()).unwrap_or("");
    let id_ = element.get("id").and_then(|v| v.as_i64()).unwrap_or(0);
    p.id = Some(format!("osm:{}/{}", type_, id_));
    
    // Type inference
    // Simplified: check for key tags
    p.type_ = "hybrid".to_string();
    if let Some(tags) = tags {
        if tags.contains_key("amenity") { p.type_ = "building".to_string(); }
        else if tags.contains_key("leisure") { p.type_ = "public_space".to_string(); }
        else if tags.contains_key("highway") { p.type_ = "street".to_string(); }
    }

    // Location
    if type_ == "node" {
        let lat = element.get("lat").and_then(|v| v.as_f64()).unwrap_or(0.0);
        let lon = element.get("lon").and_then(|v| v.as_f64()).unwrap_or(0.0);
        p.location = Some(Coordinate::new(lat, lon));
    } else if let Some(center) = element.get("center") {
         let lat = center.get("lat").and_then(|v| v.as_f64()).unwrap_or(0.0);
         let lon = center.get("lon").and_then(|v| v.as_f64()).unwrap_or(0.0);
         p.location = Some(Coordinate::new(lat, lon));
    } else if let Some(bounds) = element.get("bounds") {
        let minlat = bounds.get("minlat").and_then(|v| v.as_f64()).unwrap_or(0.0);
        let maxlat = bounds.get("maxlat").and_then(|v| v.as_f64()).unwrap_or(0.0);
        let minlon = bounds.get("minlon").and_then(|v| v.as_f64()).unwrap_or(0.0);
        let maxlon = bounds.get("maxlon").and_then(|v| v.as_f64()).unwrap_or(0.0);
        p.location = Some(Coordinate::new((minlat + maxlat)/2.0, (minlon + maxlon)/2.0));
    }

    // Boundary
    if let Some(geometry) = element.get("geometry").and_then(|v| v.as_array()) {
        for pt in geometry {
            let lat = pt.get("lat").and_then(|v| v.as_f64()).unwrap_or(0.0);
            let lon = pt.get("lon").and_then(|v| v.as_f64()).unwrap_or(0.0);
            p.boundary.push(Coordinate::new(lat, lon));
        }
    }
    
    // Purpose etc
    if let Some(tags) = tags {
        for key in ["amenity", "leisure", "shop", "tourism", "sport"] {
             if let Some(val) = tags.get(key).and_then(|v| v.as_str()) {
                 p.purpose.push(format!("{}: {}", key, val));
             }
        }
        p.source = vec![format!("OpenStreetMap ({}/{})", type_, id_)];
        
        // Extra
        for key in ["opening_hours", "website", "phone", "cuisine", "operator"] {
             if let Some(val) = tags.get(key) {
                 p.extra.insert(key.to_string(), val.clone());
             }
        }
    }
    
    p
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    println!("=== Example 1: Fetch a POI from OSM (Nottingham Castle) ===\n");
    let query_poi = r#"
[out:json][timeout:10];
node["name"="Nottingham Castle"]["tourism"](around:5000,52.9481,-1.1560);
out body;
"#;

    match overpass_query(query_poi).await {
        Ok(data) => {
             if let Some(elements) = data.get("elements").and_then(|v| v.as_array()) {
                 if !elements.is_empty() {
                     let place = osm_element_to_geon(&elements[0]);
                     println!("{}", generate(&place));
                 } else {
                     println!("No results found.");
                 }
             }
        },
        Err(e) => println!("Error fetching POI: {}", e),
    }
    
    println!("\n=== Example 2: Fetch a polygon from OSM (Wollaton Park) ===\n");
    let query_polygon = r#"
[out:json][timeout:10];
way["name"="Wollaton Park"]["leisure"="park"](around:10000,52.9481,-1.1560);
out body geom;
"#;
    match overpass_query(query_polygon).await {
         Ok(data) => {
             if let Some(elements) = data.get("elements").and_then(|v| v.as_array()) {
                 if !elements.is_empty() {
                     let place = osm_element_to_geon(&elements[0]);
                     println!("{}", generate(&place));
                 } else {
                     println!("No results found.");
                 }
             }
        },
        Err(e) => println!("Error fetching Polygon: {}", e),
    }

    Ok(())
}
