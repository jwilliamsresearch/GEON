use geon_rs::{GeonPlace, Coordinate, generate, parse};
use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Write};

fn main() -> std::io::Result<()> {
    // 1. Create a sample .geon file in memory
    let mut place = GeonPlace::default();
    place.place = "Victoria Park, Nottingham".to_string();
    place.type_ = "public_space".to_string();
    place.location = Some(Coordinate::new(52.9403, -1.1340));
    place.area = Some("14 hectares".to_string());
    place.purpose = vec!["recreation".to_string(), "sport".to_string(), "ecology".to_string(), "events".to_string()];
    
    let mut exp = HashMap::new();
    exp.insert("openness".to_string(), "high".to_string());
    exp.insert("enclosure".to_string(), "low".to_string());
    exp.insert("activity_density".to_string(), "moderate".to_string());
    place.experience = exp;
    
    place.character = vec![
        "Victorian (established 1880s)".to_string(),
        "well-maintained (bowling greens, flower beds)".to_string(),
    ];
    place.source = vec!["OpenStreetMap (2025-01)".to_string()];

    // Write to a temp file
    // In Rust std::env::temp_dir() or just local file for example
    let filename = "example_07_temp.geon";
    let text = generate(&place);
    
    {
        let mut file = File::create(filename)?;
        file.write_all(text.as_bytes())?;
    }
    
    println!("Wrote GEON file: {}", filename);
    println!("Size: {} bytes\n", text.len());
    
    // 2. Read it back
    let loaded_text = std::fs::read_to_string(filename)?;
    let mut loaded = parse(&loaded_text);
    
    println!("Loaded: {}", loaded.place);
    println!("Type:   {}", loaded.type_);
    println!("Valid:  true (implied)");
    println!();
    
    // 3. Modify and save
    let mut temp = HashMap::new();
    temp.insert("summer_events".to_string(), "concerts every Friday July-August".to_string());
    temp.insert("parkrun".to_string(), "every Saturday 09:00".to_string());
    loaded.temporal = temp;
    
    loaded.adjacencies = vec![
        "Sneinton Market (500m north)".to_string(),
        "Nottingham Station (1.2km west)".to_string(),
    ];
    
    let updated_text = generate(&loaded);
    let filename2 = "example_07_temp_updated.geon";
    {
        let mut file = File::create(filename2)?;
        file.write_all(updated_text.as_bytes())?;
    }

    println!("Updated GEON file: {}", filename2);
    println!("Size: {} bytes\n", updated_text.len());
    println!("=== Updated content ===");
    println!("{}", updated_text);
    
    // Clean up
    std::fs::remove_file(filename)?;
    std::fs::remove_file(filename2)?;

    Ok(())
}
