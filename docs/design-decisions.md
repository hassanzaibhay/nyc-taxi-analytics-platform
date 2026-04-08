# Design Decisions

## Why NYC Taxi data?
- **Scale**: hundreds of millions of rows per year — large enough to justify Spark/Hadoop.
- **Public, stable schema**: government-published, well-documented, no scraping required.
- **Industry benchmark**: widely cited in data engineering blogs and conference talks.

## Why this stack?

| Choice | Reason |
|---|---|
| Hadoop 3.4.1 | Latest stable with verified Docker image; demonstrates classic MapReduce competency. |
| Spark 3.5.4 (Bitnami) | Bitnami images are non-root, hardened, and CVE-scanned. |
| Kafka KRaft (no ZooKeeper) | Modern operational profile — one fewer service to manage. |
| Airflow 2.10.4 | Long-supported, broad provider ecosystem. |
| PostgreSQL 16 | Portable across AWS RDS / GCP Cloud SQL with zero schema changes. |
| FastAPI + asyncpg | Async I/O matches database-bound workloads; auto-generated OpenAPI. |
| React + Vite + Tailwind + Recharts | Fast iteration, no custom CSS, professional aesthetic. |
| Terraform (modular) | Same code shape for AWS and GCP; modules per service. |

## Why Docker Compose for local dev?
A single command (`make all`) brings up the whole platform on a laptop. Development feedback loops are seconds, not minutes.

## Why Terraform over CloudFormation / Deployment Manager?
Provider-agnostic syntax lets the same engineering pattern target AWS, GCP, or Azure with module swaps — important for a portfolio that demonstrates cloud-portability.

## Why Bitnami images for Spark/Kafka?
Non-root by default, regularly patched, and reproducible across environments. Apache's official images frequently lag behind on security fixes.

## Why PostgreSQL over ClickHouse / DuckDB?
PostgreSQL has first-class managed offerings on every cloud (RDS, Cloud SQL, Azure DB), while ClickHouse self-managed adds operational overhead and DuckDB is single-node only.

## Why Parquet everywhere?
Columnar layout, predicate pushdown, snappy compression, and native Spark/Hadoop support. No ad-hoc CSVs.

## Why NOT Jupyter notebooks?
This project demonstrates **engineering**, not exploration. Notebooks resist version control, hide state, and rarely make it to production. All code lives in modules with tests.
