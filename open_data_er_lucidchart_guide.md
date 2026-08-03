# Lucidchart — ERD build guide

Use this with [Lucidchart](https://www.lucidchart.com) → **Entity Relationship** template (or blank + ERD shapes).

## Quick option: Mermaid import

1. Open [Mermaid Live Editor](https://mermaid.live).
2. Paste the contents of `open_data_er_diagram.mmd`.
3. Export as **PNG** or **SVG**.
4. In Lucidchart: **Import** → image, or recreate using the diagram as reference.

Some Lucid accounts support **Mermaid** via apps/integrations—check **Import Data** in your workspace.

---

## Entities and keys (drag one table per entity)

| Entity | Primary key | Foreign keys | Main attributes |
|--------|-------------|--------------|-----------------|
| DATA_SOURCE | source_id | — | name, source_url, licence, source_update_frequency, last_ingested_at |
| SENSOR | sensor_id | source_id → DATA_SOURCE | status, notes |
| SENSOR_LOCATION_HISTORY | location_id | sensor_id → SENSOR | latitude, longitude, direction_1, direction_2, valid_from, valid_to |
| MINUTE_COUNT | (sensor_id, observed_at) | sensor_id → SENSOR | direction_1_count, direction_2_count, total_count, quality_status |
| HOURLY_COUNT | (sensor_id, observed_hour) | sensor_id → SENSOR | total_count, quality_status |
| PLACE_CATEGORY | category_id | — | theme, sub_theme |
| REFUGE_CANDIDATE | place_id | source_id → DATA_SOURCE; category_id → PLACE_CATEGORY | name, latitude, longitude, validation_status |
| ROAD_NODE | node_id | — | latitude, longitude |
| ROAD_EDGE | edge_id | from_node_id, to_node_id → ROAD_NODE | distance_m, walkable, osm_way_ref |
| CROWD_BASELINE | (sensor_id, weekday, hour_of_day) | sensor_id → SENSOR | p40_count, p75_count, sample_size, calculated_at |
| CROWD_OBSERVATION | (sensor_id, observed_at) | sensor_id → SENSOR | crowd_level, confidence, model_version |
| CROWD_PREDICTION | (sensor_id, target_hour) | sensor_id → SENSOR | predicted_level, confidence, model_version |

**Colour coding (match presentation):**

- **Imported / source facts:** DATA_SOURCE, SENSOR, SENSOR_LOCATION_HISTORY, MINUTE_COUNT, HOURLY_COUNT, PLACE_CATEGORY, REFUGE_CANDIDATE, ROAD_NODE, ROAD_EDGE  
- **Derived / analytical:** CROWD_BASELINE, CROWD_OBSERVATION, CROWD_PREDICTION  

---

## Relationships (cardinality)

| From | To | Cardinality | Label |
|------|-----|-------------|--------|
| DATA_SOURCE | SENSOR | 1 : N | provides |
| DATA_SOURCE | REFUGE_CANDIDATE | 1 : N | provides |
| DATA_SOURCE | ROAD_EDGE | 1 : N | OSM snapshot lineage |
| SENSOR | SENSOR_LOCATION_HISTORY | 1 : N | location over time |
| SENSOR | MINUTE_COUNT | 1 : N | minute readings |
| SENSOR | HOURLY_COUNT | 1 : N | hourly readings |
| SENSOR | CROWD_BASELINE | 1 : N | per weekday/hour |
| SENSOR | CROWD_OBSERVATION | 1 : N | derived levels |
| SENSOR | CROWD_PREDICTION | 1 : N | forecasts |
| PLACE_CATEGORY | REFUGE_CANDIDATE | 1 : N | classifies |
| ROAD_NODE | ROAD_EDGE | 1 : N | from_node |
| ROAD_NODE | ROAD_EDGE | 1 : N | to_node |
| HOURLY_COUNT | CROWD_BASELINE | N : M (logical) | feeds baseline job |
| CROWD_BASELINE | CROWD_PREDICTION | 1 : N | informs forecast |
| MINUTE_COUNT | CROWD_OBSERVATION | N : M (logical) | feeds classification |
| MINUTE_COUNT | CROWD_PREDICTION | N : M (logical) | recent adjustment |

Use **dashed lines** in Lucidchart for logical/ETL relationships (baseline, observation, prediction jobs) and **solid lines** for relational FKs.

---

## Layout suggestion

```
        [DATA_SOURCE]
         /    |     \
   [SENSOR]  [REFUGE]  [ROAD_EDGE]──[ROAD_NODE]
    /  |  \
[LOC_HIST] [MINUTE] [HOURLY]──┐
              |          |     └──► [CROWD_BASELINE] ──► [CROWD_PREDICTION]
              └──► [CROWD_OBSERVATION] ────────────────► (also adjusts prediction)
[PLACE_CATEGORY]──[REFUGE_CANDIDATE]
```
