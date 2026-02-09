// Data for the Hero Section Map Animation
// STRICTLY aligned with spec.md (Version 0.1.0)
// Valid TYPE values: public_space, street, building, transport_hub, infrastructure, 
//                    natural_feature, district, landmark, threshold, hybrid

const HERO_PLACES = [
    {
        name: "Nottingham Market Square",
        lat: 52.9548,
        lon: -1.1581,
        zoom: 16.5,
        text: `PLACE: Nottingham Market Square
TYPE: public_space
LOCATION: 52.9548, -1.1581
AREA: 22000 sqm
PURPOSE:
  - civic gathering
  - events
EXPERIENCE:
  openness: high
  activity_density: variable`
    },
    {
        name: "Eiffel Tower",
        lat: 48.8584,
        lon: 2.2945,
        zoom: 16,
        text: `PLACE: Eiffel Tower
TYPE: landmark
LOCATION: 48.8584, 2.2945
ELEVATION: 330m (tip)
PART_OF: Paris, France
ADJACENCIES:
  - Champ de Mars
  - River Seine
CHARACTER:
  - wrought iron construction
  - global icon
  - engineering marvel`
    },
    {
        name: "Taj Mahal",
        lat: 27.1751,
        lon: 78.0421,
        zoom: 16,
        text: `PLACE: Taj Mahal
TYPE: landmark
LOCATION: 27.1751, 78.0421
PART_OF: Agra, India
PURPOSE:
  - mausoleum
  - tourism
BUILT_FORM:
  materials: white marble
  style: Mughal architecture
CHARACTER:
  - UNESCO World Heritage Site
  - Symbol of love
  - symmetrical`
    },
    {
        name: "Sydney Opera House",
        lat: -33.8568,
        lon: 151.2153,
        zoom: 16,
        text: `PLACE: Sydney Opera House
TYPE: building
LOCATION: -33.8568, 151.2153
PART_OF: Bennelong Point, Sydney
PURPOSE:
  - performing arts centre
  - tourism
BUILT_FORM:
  architect: Jørn Utzon
  roof: shell-like structure
CHARACTER:
  - waterfront setting
  - icon of Australia`
    },
    {
        name: "Central Park",
        lat: 40.7829,
        lon: -73.9654,
        zoom: 14.5,
        text: `PLACE: Central Park
TYPE: public_space
LOCATION: 40.7829, -73.9654
PART_OF: Manhattan, New York City
AREA: 3.41 km²
PURPOSE:
  - urban park
  - recreation
CHARACTER:
  - Bethesda Terrace
  - "Lung of the city"
ECOLOGY:
  habitat_type: constructed nature
  biodiversity: diverse`
    },
    {
        name: "Uluru",
        lat: -25.3444,
        lon: 131.0369,
        zoom: 13,
        text: `PLACE: Uluru / Ayers Rock
TYPE: natural_feature
LOCATION: -25.3444, 131.0369
PART_OF: Northern Territory, Australia
ELEVATION: 863m
CHARACTER:
  - inselberg (sandstone)
  - sacred to Anangu people
  - UNESCO World Heritage
EXPERIENCE:
  visual: changes color at sunrise/sunset`
    },
    {
        name: "Varanasi Ghats",
        lat: 25.3036,
        lon: 83.0113,
        zoom: 15,
        text: `PLACE: Varanasi Ghats
TYPE: public_space
LOCATION: 25.3036, 83.0113
PART_OF: Varanasi, India
ADJACENCIES:
  - River Ganges
PURPOSE:
  - riverfront steps
  - religious ceremonies (Aarti)
  - cremation
EXPERIENCE:
  atmosphere: spiritual
  mood: chaotic / ancient`
    },
    {
        name: "Big Ben",
        lat: 51.5007,
        lon: -0.1246,
        zoom: 17,
        text: `PLACE: Elizabeth Tower (Big Ben)
TYPE: landmark
LOCATION: 51.5007, -0.1246
PART_OF: Palace of Westminster
BUILT_FORM:
  style: neo-gothic
PURPOSE:
  - clock tower
  - timekeeping
  - symbol of London`
    },
    {
        name: "CN Tower",
        lat: 43.6426,
        lon: -79.3871,
        zoom: 16,
        text: `PLACE: CN Tower
TYPE: landmark
LOCATION: 43.6426, -79.3871
ELEVATION: 553.3m
PART_OF: Toronto, Canada
PURPOSE:
  - communications tower
  - tourism
CHARACTER:
  - glass floor
  - 360 restaurant`
    },
    {
        name: "Square One",
        lat: 43.5932,
        lon: -79.6424,
        zoom: 16,
        text: `PLACE: Square One Shopping Centre
TYPE: building
LOCATION: 43.5932, -79.6424
PART_OF: Mississauga, Canada
PURPOSE:
  - commercial complex
  - retail
BUILT_FORM:
  scale: very_large
ADJACENCIES:
  - transit hub
  - urban centre`
    }
];
