use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;

/// A WGS84 coordinate pair (latitude, longitude).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Coordinate {
    pub lat: f64,
    pub lon: f64,
}

impl Coordinate {
    pub fn new(lat: f64, lon: f64) -> Self {
        Self { lat, lon }
    }

    pub fn to_geojson_position(&self) -> Vec<f64> {
        vec![self.lon, self.lat]
    }

    pub fn from_geojson_position(position: &[f64]) -> Option<Self> {
        if position.len() >= 2 {
            Some(Self {
                lat: position[1],
                lon: position[0],
            })
        } else {
            None
        }
    }
}

impl fmt::Display for Coordinate {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}, {}", self.lat, self.lon)
    }
}

/// Bounding box: north, south, east, west.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Extent {
    pub north: f64,
    pub south: f64,
    pub east: f64,
    pub west: f64,
}

impl fmt::Display for Extent {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}, {}, {}, {}", self.north, self.south, self.east, self.west)
    }
}

/// Core GEON place representation.
#[derive(Debug, Clone, PartialEq, Default, Serialize, Deserialize)]
pub struct GeonPlace {
    // --- Identity (2.2.1) ---
    #[serde(default)]
    pub place: String,
    #[serde(default)]
    pub type_: String, // "type" is a reserved keyword in Rust
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<String>,

    // --- Geometry (2.2.2) ---
    #[serde(skip_serializing_if = "Option::is_none")]
    pub location: Option<Coordinate>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub boundary: Vec<Coordinate>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extent: Option<Extent>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub elevation: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub area: Option<String>,

    // --- Semantic (2.2.3) ---
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub purpose: Vec<String>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub experience: HashMap<String, String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub character: Vec<String>,

    // --- Relational (2.2.4) ---
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub adjacencies: Vec<String>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub connectivity: HashMap<String, String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub contains: Vec<GeonPlace>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub part_of: Option<String>,
    // viewsheds can be a list or a dict in the Python version.
    // Simplifying to handling it as generic JSON or structured enum if strictly typed.
    // For now, let's treat it as a HashMap for key-value or List of strings.
    // In Python it was: list[str] | dict[str, Any].
    // Let's use an enum for better type safety or serde_json::Value.
    // Given the dynamic nature, serde_json::Value is safest for "Any".
    #[serde(default, skip_serializing_if = "is_empty_json_value")]
    pub viewsheds: serde_json::Value,

    // --- Temporal (2.2.5) ---
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub temporal: HashMap<String, String>, // Python had Any, but usage suggests str/str mostly.
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub lifespan: HashMap<String, String>,

    // --- Data provenance (2.2.6) ---
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub source: Vec<String>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub confidence: HashMap<String, String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub updated: Option<String>,

    // --- Extended / domain-specific (2.3) ---
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub built_form: HashMap<String, String>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub ecology: HashMap<String, String>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub infrastructure: HashMap<String, String>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub demographics: HashMap<String, String>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub economy: HashMap<String, String>,

    // --- Extensions (section 9) ---
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub visual: HashMap<String, String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub history: Vec<HashMap<String, String>>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub vertical_profile: HashMap<String, String>,

    // --- Catch-all for unknown / user-defined fields ---
    #[serde(flatten)]
    pub extra: HashMap<String, serde_json::Value>,
}

fn is_empty_json_value(v: &serde_json::Value) -> bool {
    v.is_null() || (v.is_array() && v.as_array().unwrap().is_empty()) || (v.is_object() && v.as_object().unwrap().is_empty())
}
