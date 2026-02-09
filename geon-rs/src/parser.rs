use crate::models::{Coordinate, Extent, GeonPlace};
use thiserror::Error;
use std::num::ParseFloatError;
use std::collections::HashMap;

#[derive(Error, Debug)]
pub enum GeonError {
    #[error("Parse error: {0}")]
    ParseFloat(#[from] ParseFloatError),
    #[error("Invalid structure: {0}")]
    InvalidStructure(String),
}

// Low-level helpers

fn indent_level(line: &str) -> usize {
    line.len() - line.trim_start().len()
}

fn split_key_value(line: &str) -> Option<(String, String)> {
    let stripped = line.trim();
    if let Some(idx) = stripped.find(':') {
        let key = stripped[..idx].trim().to_string();
        let value = stripped[idx + 1..].trim().to_string();
        Some((key, value))
    } else {
        None
    }
}

fn parse_coordinate(text: &str) -> Option<Coordinate> {
    let parts: Vec<&str> = text.split(',').map(|s| s.trim()).collect();
    if parts.len() == 2 {
        if let (Ok(lat), Ok(lon)) = (parts[0].parse::<f64>(), parts[1].parse::<f64>()) {
            return Some(Coordinate { lat, lon });
        }
    }
    None
}

// Block parser implementation

#[derive(Debug, Clone)]
enum Node {
    Value(String),
    List(Vec<Node>),
    Map(HashMap<String, Node>),
}

// Simplified approach: recursive parsing based on indentation is tricky with iterators.
// We'll use a traditional procedural approach with an index pointer.

struct Line<'a> {
    indent: usize,
    content: &'a str,
}

fn tokenize_lines(text: &str) -> Vec<Line> {
    text.lines()
        .filter(|line| !line.trim().is_empty())
        .map(|line| Line {
            indent: indent_level(line),
            content: line.trim(),
        })
        .collect()
}

// Parse a block of lines into a HashMap representing the fields
fn parse_block(lines: &[Line], start: usize, base_indent: usize) -> (HashMap<String, Node>, usize) {
    let mut result = HashMap::new();
    let mut i = start;

    while i < lines.len() {
        let line = &lines[i];
        
        if line.indent < base_indent {
            break;
        }

        // If indent > base_indent, it belongs to previous key.
        // If we are here, we expect a key at `base_indent`.
        if line.indent > base_indent {
            // Unexpected indentation or continuation of previous?
            // For this simple parser, assume we process correctly and shouldn't hit this
            // unless previous key logic failed to consume children.
            // skips...
            i += 1;
            continue;
        }

        if let Some((key, value)) = split_key_value(line.content) {
            if !value.is_empty() {
                // Simple key: value
                result.insert(key.clone(), Node::Value(value));
                i += 1;
            } else {
                // Key with children
                let (children, next_i) = collect_children(lines, i + 1, base_indent + 2);
                result.insert(key.clone(), children);
                i = next_i;
            }
        } else {
            // Not a key-value line (maybe a list item marker? handled in collect_children)
            i += 1;
        }
    }

    (result, i)
}

fn collect_children(lines: &[Line], start: usize, child_indent: usize) -> (Node, usize) {
    if start >= lines.len() {
        return (Node::List(vec![]), start);
    } // Should be empty list or map
    
    // Check if first child is list item or key-value
    let first_line = &lines[start];
    if first_line.indent < child_indent {
         return (Node::List(vec![]), start); 
    }

    let is_list = first_line.content.starts_with("- ");

    if is_list {
        let mut items = Vec::new();
        let mut i = start;
        
        while i < lines.len() {
            let line = &lines[i];
            if line.indent < child_indent {
                break;
            }
            if line.indent == child_indent && line.content.starts_with("- ") {
                let item_text = line.content[2..].trim();
                
                // Check if nested PLACE
                let kv = split_key_value(item_text);
                if let Some((k, _)) = kv {
                    if k == "PLACE" {
                         // Nested GEON block
                         // Calculate range of this block
                         let mut j = i + 1;
                         while j < lines.len() && lines[j].indent > child_indent {
                             j += 1;
                         }
                         
                         // Create a virtual block for the nested place
                         // The "PLACE: name" line serves as the header, subsequent lines are children
                         // But `parse_block` expects keys at `base_indent`.
                         // We need to fuse the current line text into the block or handle it specially.
                         // Easier: parse children as map, then insert PLACE key manually.
                         
                         // Determine field indent
                         let field_indent = if j > i + 1 { lines[i+1].indent } else { child_indent + 2 };
                         
                         let (mut sub_map, _) = parse_block(lines, i + 1, field_indent);
                         
                         // Insert the PLACE/ID/TYPE from the item_text line if present
                         if let Some((k, v)) = split_key_value(item_text) {
                            sub_map.insert(k, Node::Value(v));
                         }

                         items.push(Node::Map(sub_map));
                         i = j;
                         continue;
                    }
                }
                
                // Regular list item (scalar or object?)
                // If next line is indented further, it's an object/map attached to this item
                let mut j = i + 1;
                while j < lines.len() && lines[j].indent > child_indent {
                    j += 1;
                }
                
                if j > i + 1 {
                    // Has children
                    let field_indent = lines[i+1].indent;
                     let (mut sub_map, _) = parse_block(lines, i + 1, field_indent);
                     
                     // If item_text was "Key: Value", insert it. If just "Value", ...
                     if let Some((k, v)) = split_key_value(item_text) {
                         sub_map.insert(k, Node::Value(v));
                     } else {
                         // Handle scalar with attached map? obscure case for GEON.
                         // Usually - Value
                         //           Attr: Val
                         sub_map.insert("_value".to_string(), Node::Value(item_text.to_string()));
                     }
                     items.push(Node::Map(sub_map));
                     i = j;
                } else {
                    // Scalar list item
                    items.push(Node::Value(item_text.to_string()));
                    i += 1;
                }
                
            } else {
                // Indent match but no "- ", weird
                i += 1; 
            }
        }
        (Node::List(items), i)
    } else {
        // Map of sub-keys
        let (map, i) = parse_block(lines, start, child_indent);
        (Node::Map(map), i)
    }
}


// Converter from Node -> GeonPlace

fn node_to_string(n: &Node) -> String {
    match n {
        Node::Value(s) => s.clone(),
        Node::List(_) => "".to_string(),
        Node::Map(_) => "".to_string(),
    }
}

fn node_to_vec_string(n: &Node) -> Vec<String> {
    match n {
        Node::List(list) => list.iter().map(node_to_string).collect(),
        Node::Value(s) => vec![s.clone()],
        _ => vec![],
    }
}

fn node_to_map_string(n: &Node) -> HashMap<String, String> {
    match n {
        Node::Map(m) => {
             let mut res = HashMap::new();
             for (k, v) in m {
                 res.insert(k.clone(), node_to_string(v));
             }
             res
        },
        _ => HashMap::new(),
    }
}

fn raw_to_place(raw: HashMap<String, Node>) -> GeonPlace {
    let mut p = GeonPlace::default();
    
    if let Some(Node::Value(v)) = raw.get("PLACE") { p.place = v.clone(); }
    if let Some(Node::Value(v)) = raw.get("TYPE") { p.type_ = v.clone(); }
    if let Some(Node::Value(v)) = raw.get("ID") { p.id = Some(v.clone()); }
    
    if let Some(Node::Value(v)) = raw.get("LOCATION") { 
        p.location = parse_coordinate(v);
    }
    
    if let Some(Node::Value(v)) = raw.get("EXTENT") {
        let parts: Vec<&str> = v.split(',').map(|s| s.trim()).collect();
        if parts.len() == 4 {
             if let (Ok(n), Ok(s), Ok(e), Ok(w)) = (
                 parts[0].parse(), parts[1].parse(), parts[2].parse(), parts[3].parse()
             ) {
                 p.extent = Some(Extent { north: n, south: s, east: e, west: w });
             }
        }
    }

    if let Some(Node::Value(v)) = raw.get("ELEVATION") { p.elevation = Some(v.clone()); }
    if let Some(Node::Value(v)) = raw.get("AREA") { p.area = Some(v.clone()); }

    if let Some(n) = raw.get("PURPOSE") { p.purpose = node_to_vec_string(n); }
    if let Some(n) = raw.get("EXPERIENCE") { p.experience = node_to_map_string(n); }
    if let Some(n) = raw.get("CHARACTER") { p.character = node_to_vec_string(n); }
    
    if let Some(n) = raw.get("ADJACENCIES") { p.adjacencies = node_to_vec_string(n); }
    if let Some(n) = raw.get("CONNECTIVITY") { p.connectivity = node_to_map_string(n); }
    
    if let Some(Node::List(list)) = raw.get("CONTAINS") {
        for item in list {
            if let Node::Map(m) = item {
                p.contains.push(raw_to_place(m.clone()));
            } else if let Node::Value(s) = item {
                 // Inline string place? " - PLACE: foo" was parsed above as Map if correct.
                 // But if just string " - park", treat as bare place
                 let mut child = GeonPlace::default();
                 child.place = s.clone();
                 p.contains.push(child);
            }
        }
    }
    
    if let Some(Node::Value(v)) = raw.get("PART_OF") { p.part_of = Some(v.clone()); }
    
    // Viewsheds, Temporal, Lifespan, Source, Confidence, Updated...
    // Only implementing a subset for brevity as per plan, but complete enough for basic usage.
    // For full compliance, repeat pattern above.
    
    if let Some(n) = raw.get("TEMPORAL") { p.temporal = node_to_map_string(n); }
    if let Some(n) = raw.get("LIFESPAN") { p.lifespan = node_to_map_string(n); }
    
    // Boundary...
    if let Some(Node::List(list)) = raw.get("BOUNDARY") {
        for item in list {
            if let Node::Value(v) = item {
                if let Some(c) = parse_coordinate(v) {
                    p.boundary.push(c);
                }
            }
        }
    }

    p
}

pub fn parse(text: &str) -> GeonPlace {
    let tokens = tokenize_lines(text);
    if tokens.is_empty() {
        return GeonPlace::default();
    }
    let (raw, _) = parse_block(&tokens, 0, 0);
    raw_to_place(raw)
}
