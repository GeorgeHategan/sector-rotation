# Data

This folder stores historical sector rotation data.

## Structure

- **historical/** - CSV and JSON files from past scans

## Data Retention

Historical data files are git-ignored to keep the repository size small. Only the latest data is copied to the `docs/` folder for GitHub Pages.

## Format

- **sector_rotation_YYYYMMDD_HHMMSS.csv** - Tabular data with all metrics
- **sector_rotation_YYYYMMDD_HHMMSS.json** - JSON format for web consumption
