pub mod models;
pub mod parser;
pub mod generator;
pub mod converter;

// Re-export core items
pub use models::{GeonPlace, Coordinate, Extent};
pub use parser::parse;
pub use generator::generate;
pub use converter::from_geojson;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_coordinate_parsing() {
        let text = "LOCATION: 52.9548, -1.1581";
        let coord = parser::parse(text).location.unwrap();
        assert_eq!(coord.lat, 52.9548);
        assert_eq!(coord.lon, -1.1581);
    }

    #[test]
    fn test_simple_place() {
        let text = "PLACE: My Park\nTYPE: public_space\nLOCATION: 51.5, -0.1";
        let place = parser::parse(text);
        assert_eq!(place.place, "My Park");
        assert_eq!(place.type_, "public_space");
        let loc = place.location.unwrap();
        assert_eq!(loc.lat, 51.5);
        assert_eq!(loc.lon, -0.1);
    }

    #[test]
    fn test_nested_structure() {
        let text = r#"
PLACE: Parent
CONTAINS:
  - PLACE: Child
    TYPE: nested
    LOCATION: 1.0, 1.0
"#;
        let place = parser::parse(text);
        assert_eq!(place.place, "Parent");
        assert_eq!(place.contains.len(), 1);
        let child = &place.contains[0];
        assert_eq!(child.place, "Child");
        assert_eq!(child.type_, "nested");
    }
    
    #[test]
    fn test_nested_structure_fixed() {
        // Correcting casing to match parser implementation
        let text = r#"
PLACE: Parent
CONTAINS:
  - PLACE: Child
    TYPE: nested
    LOCATION: 1.0, 1.0
"#;
        let place = parser::parse(text);
        assert_eq!(place.place, "Parent");
        assert_eq!(place.contains.len(), 1);
        let child = &place.contains[0];
        assert_eq!(child.place, "Child");
        assert_eq!(child.type_, "nested");
    }

    #[test]
    fn test_round_trip() {
        let mut place = GeonPlace::default();
        place.place = "Test Place".to_string();
        place.type_ = "test_type".to_string();
        place.location = Some(Coordinate { lat: 10.0, lon: 20.0 });
        place.purpose = vec!["testing".to_string(), "verification".to_string()];
        
        // Generate
        let text = generate(&place);
        println!("Generated:\n{}", text);
        
        // Parse back
        let parsed = parse(&text);
        
        assert_eq!(place.place, parsed.place);
        assert_eq!(place.type_, parsed.type_);
        assert_eq!(place.location, parsed.location);
        assert_eq!(place.purpose, parsed.purpose);
    }
}
