/**
 * Data models for GEON documents.
 */

export interface Coordinate {
  lat: number;
  lon: number;
}

export interface Extent {
  north: number;
  south: number;
  east: number;
  west: number;
}

export class GeonPlace {
  // --- Identity (2.2.1) ---
  place: string = "";
  type: string = "";
  id: string | null = null;

  // --- Geometry (2.2.2) ---
  location: Coordinate | null = null;
  boundary: Coordinate[] = [];
  extent: Extent | null = null;
  elevation: string | null = null;
  area: string | null = null;

  // --- Semantic (2.2.3) ---
  purpose: string[] = [];
  experience: Record<string, string> = {};
  character: string[] = [];

  // --- Relational (2.2.4) ---
  adjacencies: string[] = [];
  connectivity: Record<string, string> = {};
  contains: GeonPlace[] = [];
  part_of: string | null = null;
  viewsheds: string[] | Record<string, any> = [];

  // --- Temporal (2.2.5) ---
  temporal: Record<string, any> = {};
  lifespan: Record<string, string> = {};

  // --- Data provenance (2.2.6) ---
  source: string[] = [];
  confidence: Record<string, string> = {};
  updated: string | null = null;

  // --- Extended / domain-specific (2.3) ---
  built_form: Record<string, any> = {};
  ecology: Record<string, any> = {};
  infrastructure: Record<string, any> = {};
  demographics: Record<string, any> = {};
  economy: Record<string, any> = {};

  // --- Extensions (section 9) ---
  visual: Record<string, any> = {};
  history: Array<Record<string, any>> = [];
  vertical_profile: Record<string, any> = {};

  // --- Catch-all for unknown / user-defined fields ---
  extra: Record<string, any> = {};
}
