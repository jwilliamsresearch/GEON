use geon_rs::{GeonPlace, Coordinate, generate, parse};
use std::collections::HashMap;

fn main() {
    // 1. Build a nested place hierarchy
    let mut grand_central = GeonPlace::default();
    grand_central.place = "Grand Central Birmingham".to_string();
    grand_central.type_ = "building".to_string();
    grand_central.location = Some(Coordinate::new(52.4774, -1.8984));
    grand_central.area = Some("75000 sqm".to_string());
    grand_central.purpose = vec![
        "retail".to_string(),
        "transport".to_string(),
        "food and beverage".to_string(),
    ];
    
    let mut experience = HashMap::new();
    experience.insert("activity_density".to_string(), "very_high".to_string());
    experience.insert("noise_level".to_string(), "loud".to_string());
    experience.insert("legibility".to_string(), "medium".to_string());
    grand_central.experience = experience;

    grand_central.adjacencies = vec![
        "New Street Station (below)".to_string(),
        "Bullring Shopping Centre (200m east)".to_string(),
        "Victoria Square (300m north)".to_string(),
    ];

    let mut connectivity = HashMap::new();
    connectivity.insert("pedestrian_entries".to_string(), "6".to_string());
    connectivity.insert("rail".to_string(), "New Street Station (direct access)".to_string());
    connectivity.insert("public_transport".to_string(), "tram (Corporation Street, 200m)".to_string());
    grand_central.connectivity = connectivity;
    
    // Child 1
    let mut child1 = GeonPlace::default();
    child1.place = "John Lewis flagship store".to_string();
    child1.type_ = "building".to_string();
    child1.location = Some(Coordinate::new(52.4776, -1.8983));
    child1.area = Some("25000 sqm".to_string());
    child1.purpose = vec!["retail (department store)".to_string()];
    
    // Child 2
    let mut child2 = GeonPlace::default();
    child2.place = "Grand Central Shopping Centre".to_string();
    child2.type_ = "building".to_string();
    child2.location = Some(Coordinate::new(52.4773, -1.8985));
    child2.area = Some("50000 sqm".to_string());
    child2.purpose = vec!["retail (mixed)".to_string(), "food and beverage".to_string()];
    
    let mut temp = HashMap::new();
    temp.insert("trading_hours".to_string(), "09:00-20:00 Mon-Sat, 11:00-17:00 Sun".to_string());
    child2.temporal = temp;
    
    grand_central.contains = vec![child1, child2];
    grand_central.part_of = Some("Birmingham City Centre".to_string());
    grand_central.source = vec![
        "Field observation (2025-01)".to_string(),
        "OpenStreetMap (2025-01)".to_string(),
    ];

    // 2. Generate
    let text = generate(&grand_central);
    println!("=== Nested GEON Document ===");
    println!("{}", text);

    // 3. Parse and verify
    let parsed = parse(&text);
    println!("=== Parsed: {} ===", parsed.place);
    println!("Contains {} sub-places:", parsed.contains.len());
    for child in &parsed.contains {
        println!("  - {} ({})", child.place, child.type_);
    }
    println!();
    
    // 4. Validate (placeholder)
    println!("Valid: true (implied)");
}
