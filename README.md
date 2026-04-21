# Teiko-Technical
Teiko Technical Problem Solution

# Clinical Trial Analysis Pipeline

## How to Run and Reproduce Results
To reproduce the analysis and launch the dashboard in GitHub Codespaces, follow these steps:
1.  **Environment Setup**: Install all required dependencies.
    ```bash
    make setup
    ```
2.  **Execute Data Pipeline**: This initializes the SQLite database, performs all the analysis, and generates output CSVs and plots.
    ```bash
    make pipeline
    ```
3.  **Launch Dashboard**: Start the interactive Dashboard to visualize the results.
    ```bash
    make dashboard
    ```
    *Once running, follow the terminal link to view the interactive dashboard.*

## Database Schema & Design Rationale

The project utilizes a relational SQLite database (`patient_samples.db`) with a normalized schema consisting of three primary tables:

1.  **`patients`**: Stores demographic data (`subject_id`, `sex`, `age`).
2.  **`samples`**: Stores metadata for each event (`sample_id`, `subject_id`, `project`, `condition`, `treatment`, `time_from_treatment_start`, `response`).
3.  **`cell_counts`**: Stores the raw counts for the five immune cell populations, linked by `sample_id`.

I applied normalization by separating patient demographics from sample metadata to avoid data redundacy. If a patient provides 10 samples over time, their gender is stored only once, which ensures the data integrity. In addition, by using the `sample_id` as a foreign key ensures all cell counts cannot exist without a corresponding metadata entry. And this schema could be optimized by indexing so in case of big data where hundreds of projects and thousands of patients are involved could be handled. Even though SQLite is fast for small projects, indexing could improve the data filtering and analysis. And the current database is ready for indexing. Filtering by baseline or specific treatment can be handled currently.

If this project scaled to **hundreds of projects** and **thousands of samples**, the fact of being relational databases can allow joining different datasets and aggregate statistics across thousands of rows in just a second. And if new analytics are required, we could add new tables linked by sample_id without restructuring the existing data. The project column also allows for easy data partitioning. It ensures researchers like Bob could analyze one specific trial or perform a meta-analysis across the entire database. 

## Code Structure & Design

The code is organized into a pipeline to ensure maintainability and clarity.

The `load_data.py` is the loading layer which reads raw CSVs, clean headers and populates the SQLite database. It ensures data types are correct and allow checking the databse before analysis begins. The `analysis.py` is the layer that calculate the relative frequencies, runs Mann-Whitney U tests for statistical significance, and exports findings to CSV and PNG files. It print out the results in addition to saving all the results and dataframes for backup and later presentations. The `dashboard.py` is the visualization layer that utilizes a Dash application and reads pre-calculated results. This design choice ensures the dashboard loads instantly because it doesn't have to perform complex SQL joins or statistical math every time a user refreshes the page. Lastly, the `Makefile` provides a unified interface for user to operate the entire program without knowing the specific filenames or order of operations.

## Dashboard Link
When running in GitHub Codespaces, the dashboard will be available at the local address provided in the terminal if the below link do not work:
**[Local Dashboard Link](http://127.0.0.1:8050)**
