"""Validation for GEON documents (Section 7 of the spec)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .models import GeonPlace
from .vocab import (
    EXPERIENCE_SCALES,
    PLACE_TYPES,
    RECOMMENDED_FIELDS,
    REQUIRED_FIELDS,
)


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    severity: Severity
    field: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.field}: {self.message}"


@dataclass
class ValidationResult:
    issues: list[Issue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        """True when there are no ERROR-level issues."""
        return not any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    def __str__(self) -> str:
        if not self.issues:
            return "Valid (no issues)"
        return "\n".join(str(i) for i in self.issues)


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def _check_required(place: GeonPlace, result: ValidationResult) -> None:
    if not place.place:
        result.issues.append(Issue(Severity.ERROR, "PLACE", "Required field PLACE is missing or empty"))
    if not place.type:
        result.issues.append(Issue(Severity.ERROR, "TYPE", "Required field TYPE is missing or empty"))
    if place.location is None:
        result.issues.append(Issue(Severity.ERROR, "LOCATION", "Required field LOCATION is missing"))


def _check_type_vocab(place: GeonPlace, result: ValidationResult) -> None:
    if place.type and place.type not in PLACE_TYPES:
        result.issues.append(
            Issue(Severity.WARNING, "TYPE", f"Type '{place.type}' is not in the controlled vocabulary: {sorted(PLACE_TYPES)}")
        )


def _check_location_range(place: GeonPlace, result: ValidationResult) -> None:
    if place.location:
        if not (-90 <= place.location.lat <= 90):
            result.issues.append(
                Issue(Severity.ERROR, "LOCATION", f"Latitude {place.location.lat} is out of range [-90, 90]")
            )
        if not (-180 <= place.location.lon <= 180):
            result.issues.append(
                Issue(Severity.ERROR, "LOCATION", f"Longitude {place.location.lon} is out of range [-180, 180]")
            )


def _check_boundary_closed(place: GeonPlace, result: ValidationResult) -> None:
    if len(place.boundary) >= 3:
        first = place.boundary[0]
        last = place.boundary[-1]
        if first.lat != last.lat or first.lon != last.lon:
            result.issues.append(
                Issue(Severity.WARNING, "BOUNDARY", "Boundary polygon is not closed (first and last coordinates differ)")
            )


def _check_experience_vocab(place: GeonPlace, result: ValidationResult) -> None:
    for key, value in place.experience.items():
        if key in EXPERIENCE_SCALES:
            # Value might contain qualifiers like "moderate (daytime)" — check base value
            base = value.split("(")[0].strip().split(",")[0].strip()
            # Allow compound values like "medium-high"
            if "-" in base:
                continue
            if base not in EXPERIENCE_SCALES[key]:
                result.issues.append(
                    Issue(
                        Severity.WARNING,
                        f"EXPERIENCE.{key}",
                        f"Value '{base}' is not in the controlled vocabulary: {list(EXPERIENCE_SCALES[key])}",
                    )
                )


def _check_recommended(place: GeonPlace, result: ValidationResult) -> None:
    field_map = {
        "PURPOSE": place.purpose,
        "EXPERIENCE": place.experience,
        "ADJACENCIES": place.adjacencies,
        "CONNECTIVITY": place.connectivity,
        "SOURCE": place.source,
    }
    for name in RECOMMENDED_FIELDS:
        value = field_map.get(name)
        if not value:
            result.issues.append(
                Issue(Severity.INFO, name, f"Recommended field {name} is empty")
            )


def _check_children(place: GeonPlace, result: ValidationResult) -> None:
    for i, child in enumerate(place.contains):
        child_result = validate(child)
        for issue in child_result.issues:
            issue.field = f"CONTAINS[{i}].{issue.field}"
            result.issues.append(issue)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate(place: GeonPlace) -> ValidationResult:
    """Validate a :class:`GeonPlace` and return a :class:`ValidationResult`.

    Checks performed (per Section 7 of the spec):
    - Required fields present (PLACE, TYPE, LOCATION)
    - Coordinate range correctness
    - Controlled vocabulary compliance for TYPE and EXPERIENCE
    - Boundary polygon closure
    - Recommended-field presence (INFO level)
    - Recursive validation of nested CONTAINS places
    """
    result = ValidationResult()
    _check_required(place, result)
    _check_type_vocab(place, result)
    _check_location_range(place, result)
    _check_boundary_closed(place, result)
    _check_experience_vocab(place, result)
    _check_recommended(place, result)
    _check_children(place, result)
    return result
