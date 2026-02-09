<p align="center"><img src="assets/logo.png" alt="GEON logo" width="280"></p>

# GEON — Geospatial Experience-Oriented Notation

**A human-curated, LLM-native format for spatial intelligence.**

GEON (Geospatial Experience-Oriented Notation) bridges the gap between machine-optimized geometric data (GeoJSON, WKT) and human-centric descriptions of place. It embeds semantic meaning, experiential qualities, and spatial relationships directly alongside coordinate data — making it the ideal currency for AI agents reasoning about the built environment.

```yaml
PLACE: Nottingham Market Square
TYPE: public_space
LOCATION: 52.9548, -1.1581
PURPOSE:
  - civic gathering
  - events and festivals
EXPERIENCE:
  openness: high
  activity_density: variable
  noise_level: moderate
ADJACENCIES:
  - Council House (immediate west)
TEMPORAL:
  weekday_footfall: 2000-3000 people/hour
```

## The GEON Philosophy

### 1. Place > Geometry
Traditional GIS formats treat the world as a collection of points, lines, and polygons. GEON treats the world as a collection of **Places**. A `PLACE` has identity, history, purpose, and feel — widely varying attributes that rigid schemas often failing to capture.

### 2. Human-in-the-Loop Curation
GEON is designed to be written and read by humans. Its indentation-based structure (resembling a clean YAML/Markdown hybrid) allows domain experts — urban planners, architects, historians — to curate spatial knowledge without fighting complex syntax (like JSON braces or XML tags).

### 3. LLM-Native Reasoning
Large Language Models excel at understanding unstructured text but struggle with dense coordinate arrays. GEON optimizes for "Semantic Density" — maximizing the amount of reasoning-relevant information per token. By explicating relationships ("ADJACENCIES") and qualities ("EXPERIENCE"), GEON gives LLMs the context they need to make high-level inferences about urban dynamics.

## Implementations

GEON is language-agnostic. Official implementations are available for:

| Language | Directory | Description |
|----------|-----------|-------------|
| **Python** | [`geon-py/`](geon-py/) | Original reference implementation. Best for data science & scripting. |
| **Rust** | [`geon-rs/`](geon-rs/) | High-performance system integration & CLIs. |
| **JavaScript** | [`geon-js/`](geon-js/) | Web & Node.js integration (TypeScript). |

Each implementation supports the full GEON spec, including fast parsing, deterministic generation, and GeoJSON interoperability.

## Conceptual Guidance

### When to use GEON?
- **Agentic Workflows**: When AI agents need to reason about a location (e.g., "Find a quiet park near a coffee shop suitable for reading").
- **Knowledge Graphs**: When building a spatial knowledge graph that connects places by semantic relationships rather than just proximity.
- **Urban Analysis**: When analyzing "soft" metrics like vibrancy, safety, or community value that aren't present in standard maps.

### When to use GeoJSON?
- **Rendering**: When you just need to draw raw shapes on a screen (Leaflet, Mapbox).
- **Storage**: When storing raw geometric primitives in a spatial database (PostGIS).

*Note: GEON includes robust converters for bi-directional compatibility with GeoJSON.*

## Ecosystem & Future Ideas

We are actively exploring tools to enhance the GEON ecosystem. Contributions are welcome!

- **CLI Tool**: A unified `geon` command-line tool (likely via `geon-rs`) for validating, formatting, and converting files.
- **IDE Support**: A VS Code extension for syntax highlighting, snippets, and live validation.
- **MCP Server**: A Model Context Protocol server to allow LLMs to natively search and read GEON repositories.
- **QGIS Plugin**: A plugin to render `.geon` files directly on QGIS canvases by converting them to GeoJSON on the fly.
- **Web Validator**: A simple drag-and-drop web app to check GEON file validity and preview its structure.

## Specification

See [`spec.md`](spec.md) for the complete version 0.1.0 specification, covering:
- **Core Fields**: `PLACE`, `TYPE`, `LOCATION`, `BOUNDARY`.
- **Semantic Fields**: `PURPOSE`, `EXPERIENCE`, `CHARACTER`.
- **Relational Fields**: `ADJACENCIES`, `CONNECTIVITY`, `CONTAINS`.
- **Temporal Fields**: `TEMPORAL`, `LIFESPAN`.

## License

GEON Specification: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
Code Implementations: MIT License
