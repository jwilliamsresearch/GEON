use crate::models::GeonPlace;
use std::fmt::Write;

const INDENT: &str = "  ";

fn write_indent(buf: &mut String, depth: usize) {
    for _ in 0..depth {
        buf.push_str(INDENT);
    }
}

fn write_line(buf: &mut String, key: &str, value: &str, depth: usize) {
    write_indent(buf, depth);
    writeln!(buf, "{}: {}", key, value).unwrap();
}

fn write_section(buf: &mut String, key: &str, depth: usize) {
    write_indent(buf, depth);
    writeln!(buf, "{}:", key).unwrap();
}

fn write_list(buf: &mut String, items: &[String], depth: usize) {
    for item in items {
        write_indent(buf, depth);
        writeln!(buf, "- {}", item).unwrap();
    }
}

fn write_dict(buf: &mut String, map: &std::collections::HashMap<String, String>, depth: usize) {
    // Sort keys for deterministic output
    let mut keys: Vec<&String> = map.keys().collect();
    keys.sort();
    
    for key in keys {
        write_indent(buf, depth);
        writeln!(buf, "{}: {}", key, map[key]).unwrap();
    }
}

fn generate_nested(buf: &mut String, place: &GeonPlace, depth: usize) {
    write_indent(buf, depth);
    writeln!(buf, "- PLACE: {}", place.place).unwrap();
    let inner = depth + 2;
    
    if !place.type_.is_empty() {
        write_line(buf, "TYPE", &place.type_, inner);
    }
    if let Some(loc) = &place.location {
        write_line(buf, "LOCATION", &loc.to_string(), inner);
    }
    if let Some(area) = &place.area {
        write_line(buf, "AREA", area, inner);
    }
    // minimal subset for nested...
}

pub fn generate(place: &GeonPlace) -> String {
    let mut buf = String::new();
    
    // Identity
    write_line(&mut buf, "PLACE", &place.place, 0);
    if !place.type_.is_empty() {
        write_line(&mut buf, "TYPE", &place.type_, 0);
    }
    if let Some(id) = &place.id {
        write_line(&mut buf, "ID", id, 0);
    }
    
    // Geometry
    if let Some(loc) = &place.location {
        write_line(&mut buf, "LOCATION", &loc.to_string(), 0);
    }
    
    if !place.boundary.is_empty() {
        write_section(&mut buf, "BOUNDARY", 0);
        let items: Vec<String> = place.boundary.iter().map(|c| c.to_string()).collect();
        write_list(&mut buf, &items, 1);
    }
    
    if let Some(ext) = &place.extent {
        write_line(&mut buf, "EXTENT", &ext.to_string(), 0);
    }
    if let Some(el) = &place.elevation {
        write_line(&mut buf, "ELEVATION", el, 0);
    }
    if let Some(area) = &place.area {
        write_line(&mut buf, "AREA", area, 0);
    }

    // Semantic
    if !place.purpose.is_empty() {
        if place.purpose.len() == 1 {
            write_line(&mut buf, "PURPOSE", &place.purpose[0], 0);
        } else {
            write_section(&mut buf, "PURPOSE", 0);
            write_list(&mut buf, &place.purpose, 1);
        }
    }
    
    if !place.experience.is_empty() {
        write_section(&mut buf, "EXPERIENCE", 0);
        write_dict(&mut buf, &place.experience, 1);
    }

    if !place.character.is_empty() {
        write_section(&mut buf, "CHARACTER", 0);
        write_list(&mut buf, &place.character, 1);
    }
    
    // Relational
    if !place.adjacencies.is_empty() {
        write_section(&mut buf, "ADJACENCIES", 0);
        write_list(&mut buf, &place.adjacencies, 1);
    }
    
    if !place.connectivity.is_empty() {
        write_section(&mut buf, "CONNECTIVITY", 0);
        write_dict(&mut buf, &place.connectivity, 1);
    }
    
    if !place.contains.is_empty() {
        write_section(&mut buf, "CONTAINS", 0);
        for child in &place.contains {
            generate_nested(&mut buf, child, 1);
        }
    }
    
    if let Some(part_of) = &place.part_of {
        write_line(&mut buf, "PART_OF", part_of, 0);
    }
    
    // Temporal
    if !place.temporal.is_empty() {
        write_section(&mut buf, "TEMPORAL", 0);
        write_dict(&mut buf, &place.temporal, 1);
    }
    if !place.lifespan.is_empty() {
        write_section(&mut buf, "LIFESPAN", 0);
        write_dict(&mut buf, &place.lifespan, 1);
    }

    // ... others ...

    buf
}
