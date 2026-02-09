use geon_rs::{GeonPlace, Coordinate, generate};
use serde_json::json;
use serde_json::Value;

// Overture category to GEON type mapping
fn overture_category_to_type(category: &str) -> String {
    let cat_lower = category.to_lowercase();
    if cat_lower.contains("restaurant") || cat_lower.contains("cafe") || cat_lower.contains("bar") || 
       cat_lower.contains("hotel") || cat_lower.contains("school") || cat_lower.contains("hospital") || 
       cat_lower.contains("bank") || cat_lower.contains("shop") || cat_lower.contains("supermarket") {
        return "building".to_string();
    }
    if cat_lower.contains("park") || cat_lower.contains("garden") || cat_lower.contains("playground") || 
       cat_lower.contains("sports_centre") || cat_lower.contains("stadium") {
        return "public_space".to_string();
    }
    if cat_lower.contains("station") || cat_lower.contains("airport") {
        return "transport_hub".to_string();
    }
    if cat_lower.contains("museum") || cat_lower.contains("monument") || cat_lower.contains("church") || 
       cat_lower.contains("cathedral") || cat_lower.contains("castle") {
        return "landmark".to_string();
    }
    "hybrid".to_string()
}

fn overture_feature_to_geon(feature: &Value) -> GeonPlace {
    let empty_val = json!({});
    let props = feature.get("properties").unwrap_or(&empty_val);
    let geom = feature.get("geometry").unwrap_or(&empty_val);
    
    let mut p = GeonPlace::default();
    
    // Name
    if let Some(names) = props.get("names").and_then(|v| v.as_object()) {
        if let Some(primary) = names.get("primary").and_then(|v| v.as_str()) {
            p.place = primary.to_string();
        } else {
            p.place = props.get("name").and_then(|v| v.as_str()).unwrap_or("Unnamed").to_string();
        }
    } else {
        p.place = props.get("name").and_then(|v| v.as_str()).unwrap_or("Unnamed").to_string();
    }
    
    // ID
    let fid = feature.get("id").and_then(|v| v.as_str()).unwrap_or("");
    let pid = props.get("id").and_then(|v| v.as_str()).unwrap_or(fid);
    p.id = Some(pid.to_string());
    
    // Category mapping
    if let Some(cats) = props.get("categories").and_then(|v| v.as_object()) {
        if let Some(main) = cats.get("main").and_then(|v| v.as_str()) {
            p.type_ = overture_category_to_type(main);
        }
        if let Some(alt) = cats.get("alternate").and_then(|v| v.as_array()) {
            p.purpose = alt.iter().filter_map(|v| v.as_str().map(|s| s.to_string())).collect();
        }
    } else {
        p.type_ = "hybrid".to_string();
    }
    
    // Location
    let gtype = geom.get("type").and_then(|v| v.as_str()).unwrap_or("");
    if gtype == "Point" {
        if let Some(coords) = geom.get("coordinates").and_then(|v| v.as_array()) {
            if coords.len() >= 2 {
                let lon = coords[0].as_f64().unwrap_or(0.0);
                let lat = coords[1].as_f64().unwrap_or(0.0);
                p.location = Some(Coordinate::new(lat, lon));
            }
        }
    }
    // Implement Polygon centroid if needed...
    
    // Confidence
    if let Some(conf) = props.get("confidence").and_then(|v| v.as_f64()) {
        p.confidence.insert("overall".to_string(), format!("{:.2}", conf));
    }
    
    // Sources
    if let Some(sources) = props.get("sources").and_then(|v| v.as_array()) {
        for src in sources {
            if let Some(dataset) = src.get("dataset").and_then(|v| v.as_str()) {
                p.source.push(format!("Overture Maps ({})", dataset));
            }
        }
    }
    if p.source.is_empty() {
        p.source.push("Overture Maps".to_string());
    }
    
    // Addresses
    if let Some(addrs) = props.get("addresses").and_then(|v| v.as_array()) {
        if !addrs.is_empty() {
            if let Some(freeform) = addrs[0].get("freeform").and_then(|v| v.as_str()) {
                p.extra.insert("address".to_string(), Value::String(freeform.to_string()));
            }
        }
    }
    
    // Website
    if let Some(websites) = props.get("websites").and_then(|v| v.as_array()) {
         if !websites.is_empty() {
             p.extra.insert("website".to_string(), websites[0].clone());
         }
    }

    p
}

fn main() {
    println!("=== Example 1: Overture Maps feature -> GEON ===\n");
    
    let overture_feature = json!({
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
                {"dataset": "meta"},
                {"dataset": "microsoft"},
            ],
            "addresses": [
                {"freeform": "1 Brewhouse Yard, Nottingham NG1 6AD"},
            ],
            "websites": ["https://www.triptojerusalem.com"],
        },
    });

    let mut place = overture_feature_to_geon(&overture_feature);
    place.character = vec![
        "historic (claims to be England's oldest inn, est. 1189)".to_string(),
        "atmospheric (carved into sandstone caves)".to_string(),
    ];
    let mut exp = std::collections::HashMap::new();
    exp.insert("enclosure".to_string(), "high".to_string());
    exp.insert("visual_complexity".to_string(), "high".to_string());
    exp.insert("sense_of_safety".to_string(), "safe".to_string());
    place.experience = exp;

    println!("{}", generate(&place));

    println!("\n=== Example 2: Overture FeatureCollection -> GEON ===\n");
    
    let overture_collection = json!({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "place-001",
                "geometry": {"type": "Point", "coordinates": [-1.1581, 52.9548]},
                "properties": {
                    "names": {"primary": "Old Market Square"},
                    "categories": {"main": "park", "alternate": ["square", "civic"]},
                    "confidence": 0.95,
                    "sources": [{"dataset": "osm"}],
                },
            },
            {
                "type": "Feature",
                "id": "place-002",
                "geometry": {"type": "Point", "coordinates": [-1.1490, 52.9534]},
                "properties": {
                    "names": {"primary": "Nottingham Castle"},
                    "categories": {"main": "castle", "alternate": ["museum", "heritage"]},
                    "confidence": 0.98,
                    "sources": [{"dataset": "osm"}, {"dataset": "microsoft"}],
                },
            },
        ],
    });

    if let Some(features) = overture_collection.get("features").and_then(|v| v.as_array()) {
        for f in features {
            let p = overture_feature_to_geon(f);
            println!("--- {} ({}) ---", p.place, p.type_);
            println!("{}", generate(&p));
        }
    }
}
