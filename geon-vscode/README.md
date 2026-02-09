# GEON for VS Code

This extension adds language support for **GEON (Geospatial Experience-Oriented Notation)**.

## Features

- **Syntax Highlighting**: Colors for GEON keywords (`PLACE:`, `TYPE:`), numbers, comments, and standard values.
- **File Association**: Automatically detecting `.geon` files.

## Installation

1. Clone the repository.
2. Navigate to `geon-vscode`.
3. Run `code --install-extension .` (requires packaging) or open the folder in VS Code and press `F5` to debug.

## Contributing

This is a basic grammar-based extension. Future updates could include:
- Snippets for common place types.
- A semantic validator using the `geon-rs` binary.
- Live preview of GeoJSON output.
