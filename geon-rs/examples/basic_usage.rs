use geon_rs::{GeonPlace, Coordinate, generate, parse};
use std::collections::HashMap;

fn main() {
    // 1. Build a GeonPlace programmatically
    let mut place = GeonPlace::default();
    place.place = "Nottingham Market Square".to_string();
    place.type_ = "public_space".to_string();
    place.location = Some(Coordinate::new(52.9548, -1.1581));
    
    place.boundary = vec![
        Coordinate::new(52.9553, -1.1592),
        Coordinate::new(52.9553, -1.1570),
        Coordinate::new(52.9543, -1.1570),
        Coordinate::new(52.9543, -1.1592),
        Coordinate::new(52.9553, -1.1592),
    ];
    
    place.area = Some("22000 sqm".to_string());
    
    place.purpose = vec![
        "civic gathering".to_string(),
        "events and festivals".to_string(),
        "informal commerce".to_string(),
        "circulation".to_string(),
    ];
    
    let mut experience = HashMap::new();
    experience.insert("openness".to_string(), "high".to_string());
    experience.insert("enclosure".to_string(), "medium".to_string());
    experience.insert("accessibility".to_string(), "high".to_string());
    experience.insert("activity_density".to_string(), "variable".to_string());
    place.experience = experience;

    place.adjacencies = vec![
        "Old Market Square tram stop (50m north)".to_string(),
        "Council House (immediate west)".to_string(),
        "Exchange Arcade (southeast corner)".to_string(),
    ];

    let mut connectivity = HashMap::new();
    connectivity.insert("pedestrian_entries".to_string(), "6".to_string());
    connectivity.insert("vehicular_access".to_string(), "restricted".to_string());
    connectivity.insert("public_transport".to_string(), "tram (adjacent)".to_string());
    place.connectivity = connectivity;

    let mut temporal = HashMap::new();
    temporal.insert("weekday_footfall".to_string(), "2000-3000 people/hour".to_string());
    temporal.insert("weekend_events".to_string(), "2-3 per month".to_string());
    temporal.insert("evening_activity".to_string(), "low (20% of daytime)".to_string());
    place.temporal = temporal;

    // 2. Generate GEON text
    let text = generate(&place);
    println!("=== Generated GEON ===");
    println!("{}", text);

    // 3. Parse it back
    let parsed = parse(&text);
    println!("=== Parsed back ===");
    println!("Place:    {}", parsed.place);
    println!("Type:     {}", parsed.type_);
    if let Some(ref loc) = parsed.location {
        println!("Location: {}", loc);
    }
    println!("Purposes: {:?}", parsed.purpose);
    println!();
    
    // 4. Validate (not implemented in Rust yet, placeholder)
    println!("=== Validation ===");
    println!("Validation not implemented in Rust version yet.");
    println!();

    // 5. Round-trip to GeoJSON (via serde_json)
    println!("=== GeoJSON ===");
    match serde_json::to_string_pretty(&parsed) {
        Ok(json) => println!("{}", json),
        Err(e) => println!("Error serializing to JSON: {}", e),
    }
}
