"""Data models for GEON documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Coordinate:
    """A WGS84 coordinate pair (latitude, longitude)."""

    lat: float
    lon: float

    def __str__(self) -> str:
        return f"{self.lat}, {self.lon}"

    def to_geojson_position(self) -> list[float]:
        """Return [longitude, latitude] for GeoJSON."""
        return [self.lon, self.lat]

    @classmethod
    def from_geojson_position(cls, position: list[float]) -> Coordinate:
        """Create from a GeoJSON [lon, lat] position."""
        return cls(lat=position[1], lon=position[0])


@dataclass
class Extent:
    """Bounding box: north, south, east, west."""

    north: float
    south: float
    east: float
    west: float

    def __str__(self) -> str:
        return f"{self.north}, {self.south}, {self.east}, {self.west}"


@dataclass
class GeonPlace:
    """Core GEON place representation.

    Required fields: place, type, location.
    All other fields are optional/recommended per the spec.
    """

    # --- Identity (2.2.1) ---
    place: str = ""
    type: str = ""
    id: str | None = None

    # --- Geometry (2.2.2) ---
    location: Coordinate | None = None
    boundary: list[Coordinate] = field(default_factory=list)
    extent: Extent | None = None
    elevation: str | None = None
    area: str | None = None

    # --- Semantic (2.2.3) ---
    purpose: list[str] = field(default_factory=list)
    experience: dict[str, str] = field(default_factory=dict)
    character: list[str] = field(default_factory=list)

    # --- Relational (2.2.4) ---
    adjacencies: list[str] = field(default_factory=list)
    connectivity: dict[str, str] = field(default_factory=dict)
    contains: list[GeonPlace] = field(default_factory=list)
    part_of: str | None = None
    viewsheds: list[str] | dict[str, Any] = field(default_factory=list)

    # --- Temporal (2.2.5) ---
    temporal: dict[str, Any] = field(default_factory=dict)
    lifespan: dict[str, str] = field(default_factory=dict)

    # --- Data provenance (2.2.6) ---
    source: list[str] = field(default_factory=list)
    confidence: dict[str, str] = field(default_factory=dict)
    updated: str | None = None

    # --- Extended / domain-specific (2.3) ---
    built_form: dict[str, Any] = field(default_factory=dict)
    ecology: dict[str, Any] = field(default_factory=dict)
    infrastructure: dict[str, Any] = field(default_factory=dict)
    demographics: dict[str, Any] = field(default_factory=dict)
    economy: dict[str, Any] = field(default_factory=dict)

    # --- Extensions (section 9) ---
    visual: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    vertical_profile: dict[str, Any] = field(default_factory=dict)

    # --- Catch-all for unknown / user-defined fields ---
    extra: dict[str, Any] = field(default_factory=dict)
