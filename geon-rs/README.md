# GEON for Rust (`geon-rs`)

A high-performance, strongly-typed Rust implementation of **GEON**.

## Overview

`geon-rs` provides a fast, safe, and efficient way to work with GEON data. It is built for:
- **System Service**: Powering backends that serve or ingest GEON data.
- **CLI Tools**: Rapidly processing large volumes of GEON files.
- **Embedded**: Suitable for environments where python is too heavy.

## Architecture

- **`models.rs`**: Defines `GeonPlace`, `Coordinate`, `Extent` using `serde` for instant JSON/Bincode serialization.
- **`parser.rs`**: A custom recursive descent parser that handles indentation-sensitive blocks without overhead.
- **`converter.rs`**: Mappings for GeoJSON <-> GEON conversion.

## Installation

Add to `Cargo.toml`:

```toml
[dependencies]
geon-rs = { path = "../geon-rs" }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

## Detailed Usage

### Parsing from File

```rust
use std::fs;
use geon_rs::parse;

let content = fs::read_to_string("data/park.geon").expect("File not found");
let place = parse(&content);

println!("Loaded: {}", place.place);
```

### Async Fetching (with `reqwest`)

See `examples/03_from_osm.rs` for a full example of querying the Overpass API and converting results to GEON structs on the fly.

### Type-Safe Fields

Unlike the dynamic Python implementation, `geon-rs` enforces types:

```rust
pub struct GeonPlace {
    pub place: String,
    pub type_: String,
    pub location: Option<Coordinate>,
    pub purpose: Vec<String>,
    pub experience: HashMap<String, String>,
    // ...
}
```

## Performance

`geon-rs` is designed to be significantly faster than the Python implementation (benchmarks pending). It avoids regex for critical parsing paths and uses direct string manipulation.

## Examples

| Example | Command | Description |
|---------|---------|-------------|
| **Basic** | `cargo run --example 01_basic_usage` | CRUD operations. |
| **GeoJSON** | `cargo run --example 02_from_geojson` | Conversion logic. |
| **OSM** | `cargo run --example 03_from_osm` | Live API fetching. |
| **Overture** | `cargo run --example 04_from_overture` | Overture Maps schema mapping. |
| **IO** | `cargo run --example 07_file_io` | File reading/writing. |
