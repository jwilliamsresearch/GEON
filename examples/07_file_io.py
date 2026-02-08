"""Read and write .geon files.

Demonstrates loading GEON from disk, modifying, and saving back.
No external dependencies required.
"""

import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import geon

# ── Create a sample .geon file ────────────────────────────────────────────

place = geon.GeonPlace(
    place="Victoria Park, Nottingham",
    type="public_space",
    location=geon.Coordinate(52.9403, -1.1340),
    area="14 hectares",
    purpose=["recreation", "sport", "ecology", "events"],
    experience={
        "openness": "high",
        "enclosure": "low",
        "activity_density": "moderate",
    },
    character=[
        "Victorian (established 1880s)",
        "well-maintained (bowling greens, flower beds)",
    ],
    source=["OpenStreetMap (2025-01)"],
)

# Write to a temp file
tmp = tempfile.NamedTemporaryFile(suffix=".geon", mode="w", delete=False, encoding="utf-8")
text = geon.generate(place)
tmp.write(text)
tmp.close()

print(f"Wrote GEON file: {tmp.name}")
print(f"Size: {len(text)} bytes\n")

# ── Read it back ──────────────────────────────────────────────────────────

with open(tmp.name, encoding="utf-8") as f:
    loaded = geon.parse(f.read())

print(f"Loaded: {loaded.place}")
print(f"Type:   {loaded.type}")
print(f"Valid:  {geon.validate(loaded).valid}")
print()

# ── Modify and save ───────────────────────────────────────────────────────

loaded.temporal = {
    "summer_events": "concerts every Friday July-August",
    "parkrun": "every Saturday 09:00",
}
loaded.adjacencies = [
    "Sneinton Market (500m north)",
    "Nottingham Station (1.2km west)",
]

updated_text = geon.generate(loaded)
tmp2 = tempfile.NamedTemporaryFile(suffix=".geon", mode="w", delete=False, encoding="utf-8")
tmp2.write(updated_text)
tmp2.close()

print(f"Updated GEON file: {tmp2.name}")
print(f"Size: {len(updated_text)} bytes\n")
print("=== Updated content ===")
print(updated_text)

# Clean up
os.unlink(tmp.name)
os.unlink(tmp2.name)
