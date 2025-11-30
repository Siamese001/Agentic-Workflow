# Data Directory Structure

This directory contains all data assets for the Agentic Workflow L5 system, organized into a hierarchical structure supporting resume processing, outreach campaigns, and runtime operations.

## Directory Structure

### `production_inputs/`

Input data for production workflows and user operations.

#### `master_resume/`

- `resume_master.md` - Master resume content in Markdown format
- `resume_metadata.json` - Resume metadata, skills, and structured information

#### `job_descriptions/`

- `jd_001.txt`, `jd_002.txt` - Job description text files for analysis and matching

#### `outreach_targets/`

- `target_list.csv` - Contact and company target lists
- `org_profiles.yaml` - Organization profiles and company information

#### `user_profiles/`

- `persona.yaml` - User persona and communication preferences
- `constraints.yaml` - User constraints and requirements

### `datasets/`

Reference datasets and training data for the agentic system.

#### `taxonomies/`

- `skills_v1.yaml` - Skills taxonomy and classification system
- `industries.yaml` - Industry classifications and mappings
- `seniority_map.yaml` - Role seniority level definitions

#### `embeddings/`

- `skill_embeddings.json` - Pre-computed skill vector embeddings
- `jd_cluster_centroids.npy` - Job description cluster centroids (binary format)

#### `corpora/`

- `outreach_examples.json` - Example outreach messages and templates
- `resume_examples.json` - Sample resumes for training and validation

### `golden_sets/`

Reference datasets for testing, validation, and quality assurance.

#### `resume_engine/`

- `golden_resumes.json` - Benchmark resume examples with expected outputs
- `golden_scores.json` - Expected scoring results for validation

#### `outreach_engine/`

- `golden_messages.json` - Reference outreach messages for quality testing
- `golden_archetypes.json` - Contact archetype classifications and weights

#### `common/`

- `sanity_tests.json` - System sanity test data and expected results
- `quality_baselines.json` - Quality benchmarks and baseline metrics

### `tmp_runtime/`

Runtime data directories (excluded from version control).

#### `scratchpad/`

Temporary workspace for intermediate processing results.
*Note: Contents are not tracked in git.*

#### `cache/`

System cache for optimized performance.
*Note: Contents are not tracked in git.*

### `lookups/`

Reference lookup tables and mapping files.

- `stopwords.txt` - Text processing stopwords list
- `country_codes.yaml` - Country code mappings and validation
- `degree_map.yaml` - Academic degree normalization mappings
- `title_normalization.yaml` - Job title standardization rules

## File Formats

- **YAML (.yaml/.yml)** - Configuration and structured data
- **JSON (.json)** - Structured data and API responses
- **TXT (.txt)** - Plain text content and documents
- **CSV (.csv)** - Tabular data and contact lists
- **NPY (.npy)** - NumPy binary arrays for embeddings

## Usage Guidelines

1. **Production Inputs**: Modify these files to customize system behavior for specific users or campaigns
2. **Datasets**: Reference data that should not be modified without proper validation
3. **Golden Sets**: Used for automated testing - maintain consistency with expected outputs
4. **Runtime Directories**: Automatically managed by the system - do not manually edit
5. **Lookups**: Reference tables for data normalization and validation

## Data Integrity

- All configuration files should follow the schemas defined in `config/validation/schema_registry.yaml`
- Golden sets are used for regression testing and quality assurance
- Runtime data is automatically cleaned up based on retention policies

## Security Considerations

- Production inputs may contain sensitive user data
- Follow PII detection and filtering rules defined in L5 safety configurations
- Runtime directories are excluded from version control to prevent accidental data exposure
