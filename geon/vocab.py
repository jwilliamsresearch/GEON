"""Controlled vocabularies for GEON format fields."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 3.1  Place Types
# ---------------------------------------------------------------------------

PLACE_TYPES: set[str] = {
    "public_space",
    "street",
    "building",
    "transport_hub",
    "infrastructure",
    "natural_feature",
    "district",
    "landmark",
    "threshold",
    "hybrid",
}

# ---------------------------------------------------------------------------
# 3.2  Experiential Qualities
# ---------------------------------------------------------------------------

FIVE_SCALE = ("very_low", "low", "medium", "high", "very_high")
NOISE_SCALE = ("very_quiet", "quiet", "moderate", "loud", "very_loud")
COMPLEXITY_SCALE = ("very_simple", "simple", "moderate", "complex", "very_complex")
AIR_QUALITY_SCALE = ("very_poor", "poor", "moderate", "good", "very_good")
ACTIVITY_DENSITY_SCALE = ("deserted", "sparse", "moderate", "busy", "crowded")
SAFETY_SCALE = ("very_unsafe", "unsafe", "neutral", "safe", "very_safe")
TERRITORIALITY_SCALE = ("very_private", "semi_private", "semi_public", "public", "very_public")
PACE_SCALE = ("very_slow", "slow", "moderate", "fast", "very_fast")
STABILITY_SCALE = ("very_transient", "transient", "stable", "permanent", "very_permanent")

# Map from experience key → valid values
EXPERIENCE_SCALES: dict[str, tuple[str, ...]] = {
    # Spatial qualities
    "openness": FIVE_SCALE,
    "enclosure": FIVE_SCALE,
    "permeability": FIVE_SCALE,
    "legibility": FIVE_SCALE,
    # Sensory qualities
    "noise_level": NOISE_SCALE,
    "visual_complexity": COMPLEXITY_SCALE,
    "air_quality": AIR_QUALITY_SCALE,
    # Social qualities
    "activity_density": ACTIVITY_DENSITY_SCALE,
    "social_diversity": FIVE_SCALE,
    "sense_of_safety": SAFETY_SCALE,
    "territoriality": TERRITORIALITY_SCALE,
    # Temporal qualities
    "pace": PACE_SCALE,
    "temporal_stability": STABILITY_SCALE,
}

# ---------------------------------------------------------------------------
# 3.3  Purpose Categories
# ---------------------------------------------------------------------------

PURPOSE_CATEGORIES: dict[str, list[str]] = {
    "Economic": ["commerce", "retail", "services", "production", "agriculture"],
    "Civic": ["governance", "community", "education", "health", "emergency"],
    "Social": ["gathering", "celebration", "protest", "exchange", "encounter"],
    "Cultural": ["arts", "heritage", "performance", "exhibition", "worship"],
    "Recreational": ["play", "sport", "leisure", "contemplation", "exercise"],
    "Residential": ["dwelling", "sleeping", "domesticity"],
    "Circulation": ["movement", "waiting", "transition", "parking"],
    "Ecological": ["habitat", "biodiversity", "environmental services"],
}

ALL_PURPOSES: set[str] = {p for purposes in PURPOSE_CATEGORIES.values() for p in purposes}

# ---------------------------------------------------------------------------
# Required / recommended fields
# ---------------------------------------------------------------------------

REQUIRED_FIELDS: tuple[str, ...] = ("PLACE", "TYPE", "LOCATION")
RECOMMENDED_FIELDS: tuple[str, ...] = ("PURPOSE", "EXPERIENCE", "ADJACENCIES", "CONNECTIVITY", "SOURCE")
