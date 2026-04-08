# Data Dictionary — NYC Yellow Taxi Trip Records

Source: [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

## Raw Parquet Fields

| Field | Type | Description |
|---|---|---|
| VendorID | int | Provider that supplied the record (1=Creative Mobile, 2=VeriFone). |
| tpep_pickup_datetime | timestamp | Meter engaged. |
| tpep_dropoff_datetime | timestamp | Meter disengaged. |
| passenger_count | int | Driver-entered passenger count. |
| trip_distance | double | Miles, from taximeter. |
| RatecodeID | int | 1=Standard, 2=JFK, 3=Newark, 4=Nassau/Westchester, 5=Negotiated, 6=Group. |
| store_and_fwd_flag | string | Y/N — held in vehicle memory before transmission. |
| PULocationID | int | TLC taxi zone where meter engaged. |
| DOLocationID | int | TLC taxi zone where meter disengaged. |
| payment_type | int | 1=Credit, 2=Cash, 3=No charge, 4=Dispute, 5=Unknown, 6=Voided. |
| fare_amount | double | Time-and-distance fare. |
| extra | double | Miscellaneous extras (e.g. rush hour). |
| mta_tax | double | $0.50 NY tax. |
| tip_amount | double | Tip (credit only — cash tips not recorded). |
| tolls_amount | double | Sum of tolls paid. |
| improvement_surcharge | double | $0.30 surcharge. |
| total_amount | double | Total charged to passenger (excluding cash tips). |
| congestion_surcharge | double | NYS congestion surcharge. |
| airport_fee | double | LGA / JFK fee. |

## Derived Analytics Fields

| Field | Source | Description |
|---|---|---|
| hour_start | derived | `date_trunc('hour', tpep_pickup_datetime)`. |
| trip_count | aggregation | Count of trips per (zone, hour). |
| avg_fare | aggregation | Mean fare amount in window. |
| avg_tip_percentage | derived | `tip_amount / fare_amount * 100`, then averaged. |
| total_revenue | aggregation | `SUM(total_amount)`. |
| zone_pair | derived | `concat(PULocationID, '-', DOLocationID)`. |
| distance_bucket | derived | short / medium / long / very_long. |
