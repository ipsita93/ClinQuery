# ClinQuery — Clinical Research Cohort & Data Intelligence Platform

**ClinQuery** is a small, public-safe demonstration of an end-to-end clinical research data workflow: transforming synthetic clinical data into research-ready datasets, building analytical marts, defining patient cohorts, validating data quality, and providing researcher-facing access to the results.

The project is designed to demonstrate practical skills in **clinical research informatics, healthcare data engineering, SQL, Python, data modeling, ETL, and analytical workflows**.

> **Important:** All data in this repository is synthetic. No real patient data, credentials, or protected health information (PHI) are included.

## What ClinQuery demonstrates

```text
Synthetic Clinical Data
        ↓
Data Ingestion & Transformation
        ↓
OMOP-inspired Research Model
        ↓
DuckDB Research Warehouse
        ↓
Data Quality Validation
        ↓
Research Cohort Queries
        ↓
Researcher-facing Dashboard
```

### Key capabilities

* **Clinical data modeling** using OMOP-style concepts and tables
* **ETL/data transformation** using Python and SQL
* **Research data warehouse** implemented with DuckDB
* **dbt models** for reproducible transformations
* **Cohort definition** using clinical inclusion/exclusion criteria
* **Data quality checks** for research datasets
* **Population-level analysis** including condition trends and geographic prevalence
* **Researcher-facing queries** for exploring clinical cohorts
* Lightweight web dashboard for exploring results
* Optional **MCP interface** for natural-language access to approved data functions

## Clinical research use case

ClinQuery simulates a common clinical research informatics workflow.

A researcher may want to answer questions such as:

* How many patients meet a particular clinical cohort definition?
* What is the prevalence of hypertension across counties?
* How do chronic disease trends change over time?
* Which patients with Type 2 diabetes had emergency-room visits?
* What data-quality issues could affect a research analysis?

The application translates these questions into controlled queries against a research-oriented data mart rather than allowing unrestricted access to the underlying database.

## Data model

The project uses synthetic data organized around an **OMOP-inspired structure**, including:

* `person`
* `visit_occurrence`
* `condition_occurrence`
* `drug_exposure`
* `concept`
* `location`

The transformation layer creates analytical marts including:

* Patient-level chronic disease cohorts
* Condition trends by year
* County-level prevalence
* Data-quality indicators

This is a demonstration of the concepts and workflow rather than a distribution of the OMOP vocabulary or a production implementation of an institutional clinical research warehouse.

## Technology stack

| Layer           | Technology                       |
| --------------- | -------------------------------- |
| Programming     | Python                           |
| Querying        | SQL                              |
| Database        | DuckDB                           |
| Transformation  | dbt                              |
| Data modeling   | OMOP-inspired clinical model     |
| Frontend        | HTML / CSS / JavaScript          |
| Visualization   | Chart.js                         |
| Data access     | Controlled query functions / MCP |
| Version control | Git / GitHub                     |

## Repository structure

```text
ClinQuery/
├── data/
│   ├── raw/                 # Synthetic clinical data
│   └── warehouse/           # DuckDB research warehouse
│
├── src/                     # Application and data-access logic
├── scripts/                 # Data generation and pipeline scripts
├── transform/               # dbt models
├── reports/                 # Example research outputs
├── docs/                    # Architecture and methodology
└── README.md
```

## Run locally

### 1. Create the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate the synthetic data and warehouse

```bash
python scripts/generate_omop_sample.py
python scripts/build_warehouse.py
python scripts/write_report.py
```

### 4. Start the application

```bash
python -m src.api
```

Then open:

**http://127.0.0.1:8000**

Example questions include:

* How many patients are in the cohort?
* What is hypertension prevalence by county?
* Show data quality issues.
* Find Type 2 diabetes patients with ER visits.
* Look up diabetes patients in San Francisco.

## Data quality

The project includes a dedicated data-quality mart with intentionally introduced issues.

This allows the project to demonstrate an important clinical research informatics principle:

> A research dataset is only useful when researchers can understand and trust its quality.

The quality checks cover issues such as missing values, inconsistent records, and other conditions that could affect downstream research analyses.

## Optional dbt transformation layer

The `transform/` directory expresses the analytical transformations as dbt models.

The default configuration is designed to work locally with DuckDB, while `profiles.yml.example` illustrates how the same conceptual transformation layer could be adapted to a Snowflake environment.

The application itself does **not** require dbt to run.

## MCP interface

ClinQuery also includes an optional Model Context Protocol (MCP) interface.

The MCP tools expose a controlled set of data-access functions such as:

* `ask_data`
* `get_overview`
* `lookup_patients`

The intent is to demonstrate how natural-language interfaces can be placed on top of **auditable, explicitly defined data-access functions**, rather than allowing an AI system unrestricted database access.

## Project documentation

* [Architecture](docs/architecture.md) — system design and data flow
* [OMOP & OHDSI](docs/omop_and_ohdsi.md) — clinical data model context
* [Interview Talking Points](docs/interview_talking_points.md) — technical decisions and discussion points
* [MCP & Snowflake](docs/mcp_and_snowflake.md) — optional extensions
* [Sample Findings](reports/sample_findings.md) — example analytical outputs

## Design principles

### 1. Public-safe by design

All data is synthetic so the project can be shared publicly without exposing patient information.

### 2. Research-first data modeling

The data model is designed around common clinical research questions rather than simply displaying raw clinical records.

### 3. Reproducible transformations

Data preparation and analytical transformations are represented as code so that the workflow can be reproduced.

### 4. Data quality matters

The project intentionally includes quality issues to demonstrate how data validation fits into a clinical research pipeline.

### 5. Controlled data access

Researcher-facing queries are implemented through defined functions and allowlisted operations, providing a more auditable approach to natural-language data exploration.

## Disclaimer

This project is an educational and portfolio demonstration using synthetic data. It is not a production clinical research data warehouse, does not contain real patient information, and does not represent an institutional implementation of Epic, OMOP, or any specific health system's clinical data environment.

MIT License.
