import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

def analyze_cell_frequencies(db_path='patient_samples.db'):

    conn = sqlite3.connect(db_path)
    #query the table, include response for later dashboard
    query = """
    SELECT c.*, s.response 
    FROM cell_counts c
    JOIN samples s ON c.sample_id = s.sample_id
    """
    df_counts = pd.read_sql_query(query, conn)
    conn.close()

    cell_population = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']

    #obtain total counts
    df_counts['total_count'] = df_counts[cell_population].sum(axis=1)

    #change format into two columns: population and count
    df_long = df_counts.melt(
        id_vars=['sample_id', 'total_count', 'response'],
        value_vars=cell_population,
        var_name='population',
        value_name='count'
    )

    #calculate
    df_long['percentage'] = (df_long['count'] / df_long['total_count']) * 100

    #rename and sort
    df_long = df_long.rename(columns={'sample_id': 'sample'})
    df_long = df_long.sort_values(by=['sample', 'population']).reset_index(drop = True)


    #display the table and save
    df_long.to_csv('cell_frequency_analysis.csv', index=False)
    print(df_long)
    

    return df_long


def analyze_treatment_response(db_path='patient_samples.db'):
    conn = sqlite3.connect(db_path)
    
    # filter out the data wanted: PBMC data samples, melanoma patient
    query = """
    SELECT 
        c.sample_id, 
        c.b_cell, c.cd8_t_cell, c.cd4_t_cell, c.nk_cell, c.monocyte,
        s.response
    FROM cell_counts c
    JOIN samples s ON c.sample_id = s.sample_id
    WHERE s.condition = 'melanoma' 
      AND s.treatment = 'miraclib'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    cell_populations = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    
    #calculate freq
    df['total_count'] = df[cell_populations].sum(axis=1)
    for pop in cell_populations:
        df[f'{pop}_pct'] = (df[pop] / df['total_count']) * 100

    #run statistical test
    results = []
    for pop in cell_populations:
        responders = df[df['response'] == 'yes'][f'{pop}_pct']
        non_responders = df[df['response'] == 'no'][f'{pop}_pct']
        
        #run the Mann-Whitney U Test
        stat, p_value = mannwhitneyu(responders, non_responders)
        
        results.append({
            'population': pop,
            'p_value': p_value,
            'significant': 'Yes' if p_value < 0.05 else 'No'
        })

    stats_df = pd.DataFrame(results)
    stats_df.to_csv('statistical_analysis.csv', index=False)
    print(stats_df)

    #plot boxplots
    #reshape the df
    plot_df = df.melt(id_vars=['response'], value_vars=[f'{p}_pct' for p in cell_populations],var_name='population', value_name='percentage')
    plot_df['population'] = plot_df['population'].str.replace('_pct', '')

    plt.figure(figsize=(12, 6))
    sns.boxplot(data=plot_df, x='population', y='percentage', hue='response')
    plt.title('Immune Cell Frequencies: Responders vs Non-Responders')
    plt.ylabel('Relative Frequency(%)')
    plt.xlabel('Cell Population')
    
    #save the plot
    plt.savefig('response_comparison_boxplot.png')
    
    return stats_df

def analyze_baseline_subset(db_path='patient_samples.db'):
    conn = sqlite3.connect(db_path)
    
    #filter for melanoma condition, miraclib treatment, Day 0
    #join samples and patients to get gender and response data
    query = """
    SELECT 
        s.project,
        s.sample_id,
        s.subject_id,
        s.response,
        p.sex,
        s.condition,
        s.treatment,
        s.time_from_treatment_start
    FROM samples s
    JOIN patients p ON s.subject_id = p.subject_id
    WHERE s.condition = 'melanoma'
      AND s.treatment = 'miraclib'
      AND s.time_from_treatment_start = 0
    """
    baseline_df = pd.read_sql_query(query, conn)
    
    if baseline_df.empty:
        print("No baseline samples found.")
        conn.close()
        return
    
    output_filename = 'melanoma_miraclib_baseline_data.csv'
    baseline_df.to_csv(output_filename, index=False)
    print(f"Baseline data saved to: {output_filename}")

    total_baseline_samples = len(baseline_df)
    print(f"Total baseline samples identified: {total_baseline_samples}")

    #samples per project
    project_counts = baseline_df['project'].value_counts()
    print("\nSamples per Project:")
    print(project_counts.to_string())

    #responders vs non-responders 
    response_counts = baseline_df.groupby('response')['subject_id'].nunique()
    print("\nSubject Response Breakdown:")
    print(response_counts.to_string())

    #gender breakdown
    gender_counts = baseline_df.groupby('sex')['subject_id'].nunique()
    print("\nSubject Gender Breakdown:")
    print(gender_counts.to_string())

    conn.close()

if __name__ == "__main__":
    analyze_cell_frequencies() 
    analyze_treatment_response()
    analyze_baseline_subset()