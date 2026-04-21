import sqlite3
import pandas as pd
import os

def load_data():
    csv_file = 'cell-count.csv'
    db_file = 'patient_samples.db'

    df = pd.read_csv(csv_file)

    # use sqlite to model the data
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS patients (
            subject_id TEXT PRIMARY KEY,
            sex TEXT,
            age INTEGER
        );

        CREATE TABLE IF NOT EXISTS samples (
            sample_id TEXT PRIMARY KEY,
            patient_id TEXT,
            project TEXT,
            condition TEXT,
            treatment TEXT,
            time_from_treatment_start INTEGER,
            response TEXT,
            FOREIGN KEY (subject_id) REFERENCES patients (subject_id)
        );

        CREATE TABLE IF NOT EXISTS cell_counts (
            sample_id TEXT PRIMARY KEY,
            b_cell REAL,
            cd8_t_cell REAL,
            cd4_t_cell REAL,
            nk_cell REAL,
            monocyte REAL,
            FOREIGN KEY (sample_id) REFERENCES samples (sample_id)
        );
    ''')

    # load data in
    patients_df = df[['subject', 'sex', 'age']].drop_duplicates(subset=['subject'])
    patients_df.columns = ['subject_id', 'sex', 'age']
    patients_df.to_sql('patients', conn, if_exists='replace', index=False)

    #samples
    samples_df = df[['sample', 'subject', 'project', 'condition', 'treatment', 'time_from_treatment_start', 'response']]
    samples_df.columns = ['sample_id', 'subject_id', 'project', 'condition', 'treatment', 'time_from_treatment_start', 'response']
    samples_df.to_sql('samples', conn, if_exists='replace', index=False)

    #cell counts
    counts_columns = ['sample', 'b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    counts_df = df[counts_columns]
    counts_df.columns = ['sample_id', 'b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    counts_df.to_sql('cell_counts', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()
    print(f"Successfully generated {db_file} and loaded data from {csv_file}.")

if __name__ == "__main__":
    load_data()