# 📦 Ecommerce Data Warehouse Project: ETL, Data Cleansing & Relational Modeling

This project aims to build an end-to-end data ingestion, cleaning, and loading pipeline for real-world ecommerce data into a relational Data Warehouse using Python, pandas, and PostgreSQL.

## 🚀 Context & Goal

Online stores generate valuable data daily: customers, orders, products, payments, shipping, and more.  
But in practice, **extracting, organizing, and analyzing this data** can be a huge challenge, especially when:

- Exported reports come in inconsistent formats.
- Essential columns come with different names or are missing.
- There are missing values, duplicates, or typos.
- Relationships are not clear (e.g., orders that don’t match clients or products).

**The goal of this project was to turn this chaos into a clean, reliable, relational database ready for advanced analytics!**

---

## 🛠️ ETL Pipeline

The project is divided into three main steps, with separate scripts:

1. **load_staging.py:** Reads and standardizes the original files (`orders`, `clients`, `products`) exported from the ecommerce platform, saving them as CSV in the staging layer.

2. **transform.py:** Applies extensive data cleaning and transformation techniques:
   - Standardizes column names and types.
   - Parses dates and numeric values, handling formatting issues (e.g., comma as decimal separator).
   - Fills missing values and normalizes product variations.
   - Removes duplicates, validates keys and relationships.
   - Generates the final tables: `dim_cliente`, `dim_produto`, `fato_vendas`.

3. **load_to_db.py:** Loads the cleaned data into the PostgreSQL database, enforcing referential integrity and foreign keys.

---

## 🧹 Data Quality Challenges & Cleaning

During this project, several real-world data quality issues had to be solved, including:

- **Dates in multiple formats:** dates with/without time, different order, time zone usage or not.  
  _Solution:_ Robust parsing with pandas and best-effort detection.
- **Numeric values with commas:** monetary/quantity fields exported as strings like `"49,9"` instead of `49.9`.  
  _Solution:_ Programmatic replacement of commas and safe conversion to float.
- **Duplicates:** clients with the same CPF or products with the same SKU appearing multiple times.  
  _Solution:_ Deduplication, always keeping the most recent record.
- **Missing keys:** products referenced in sales but missing from the product table (possibly deleted from the platform).  
  _Solution:_ Inconsistency reporting and blocking those records to preserve referential integrity.
- **Missing columns and inconsistent names:** required mapping and standardization to make sure the DDL and DataFrames matched.

---

## 💾 Relational Modeling (DDL)

The model follows a Data Warehouse best-practice, with client and product dimensions and a fact table for sales, including foreign keys for referential integrity. [See the full DDL in `ddl.sql`.](./ddl.sql)

---

## 🔍 Key Lessons & Achievements

- The importance of a robust data-cleaning pipeline able to handle unexpected errors from real-life ecommerce exports.
- **Referential integrity is non-negotiable:** it’s not enough to load data—it needs to connect!
- Keeping error logs and inconsistency reports is part of serious data engineering work.
- The value of documenting the process for easier maintenance and scalability.

---

## 🗂️ Project Structure

### What each folder/file means:

- **data/import_manual/**: Ecommerce platform files.
- **data/staging/**: Intermediate step – the files here have unified columns, fixed encodings, etc. Used for reproducibility.
- **data/processed/**: These are the files after all data cleaning. They are ready to be loaded into the database.
- **scripts/etl/load_staging.py**: Reads and standardizes the raw exports.
- **scripts/etl/transform.py**: Cleans, validates, deduplicates, and prepares all data, handling real-life errors and inconsistencies.
- **scripts/etl/load_to_db.py**: Loads the final data into the database, making sure referential integrity and all keys are respected.
- **ddl.sql**: The database schema definition (tables, columns, constraints, keys).
- **.env**: Place for DB connection string and sensitive info (never commit secrets in public repos!).
- **README.md**: This guide and project summary.

---
