import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import os
import json

def menu():
    print("\nTMDB Movies Data Visualization Menu:")
    print("1. Distribution of Movie Budgets")
    print("2. Distribution of Movie Revenues")
    print("3. Distribution of Runtimes")
    print("4. Top Genres (Bar Plot)")
    print("5. Average Rating by Genre")
    print("6. Movies Released per Year")
    print("7. Top 10 Movies by Vote Count")
    print("8. Distribution of Popularity")
    print("0. Exit")
    return input("Select an option: ")


def plot_ratings_distribution(conn):
    df = pd.read_sql_query('''SELECT r.averageRating FROM title_ratings r JOIN title_basics b ON r.tconst = b.tconst WHERE b.titleType = 'movie' ''', conn)
    sns.histplot(df['averageRating'], bins=10, kde=True)
    plt.title('Distribution of Movie Ratings')
    plt.xlabel('Average Rating')
    plt.ylabel('Count')
    plt.show()

def plot_genre_counts(conn):
    df = pd.read_sql_query("SELECT genres FROM title_basics WHERE titleType = 'movie' AND genres != '\\N'", conn)
    # Split and flatten all genres
    genre_list = []
    for genres in df['genres']:
        if genres:
            genre_list.extend([g.strip() for g in genres.split(',') if g.strip()])
    from collections import Counter
    genre_counts = Counter(genre_list)
    genre_df = pd.DataFrame(genre_counts.items(), columns=['Genre', 'Count']).sort_values('Count', ascending=False)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=genre_df, x='Genre', y='Count', hue='Genre', palette='viridis', legend=False)
    plt.title('Movie Genre Counts')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def plot_avg_rating_by_genre(conn):
    df = pd.read_sql_query('''SELECT b.genres, r.averageRating FROM title_basics b JOIN title_ratings r ON b.tconst = r.tconst WHERE b.titleType = 'movie' AND b.genres != '\\N' ''', conn)
    rows = []
    for _, row in df.iterrows():
        for genre in row['genres'].split(','):
            rows.append({'Genre': genre.strip(), 'Rating': row['averageRating']})
    genre_df = pd.DataFrame(rows)
    avg_df = genre_df.groupby('Genre')['Rating'].mean().reset_index().sort_values('Rating', ascending=False)
    sns.barplot(data=avg_df, x='Genre', y='Rating')
    plt.title('Average Movie Rating by Genre')
    plt.xticks(rotation=45)
    plt.show()

def plot_movies_per_year(conn):
    df = pd.read_sql_query("SELECT startYear FROM title_basics WHERE titleType = 'movie' AND startYear != '\\N'", conn)
    df['startYear'] = pd.to_numeric(df['startYear'], errors='coerce')
    sns.histplot(df['startYear'], bins=30)
    plt.title('Number of Movies per Year')
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.show()

def plot_top10_highest_rated(conn):
    df = pd.read_sql_query('''SELECT b.primaryTitle, r.averageRating, r.numVotes FROM title_basics b JOIN title_ratings r ON b.tconst = r.tconst WHERE b.titleType = 'movie' AND r.numVotes > 1000 ORDER BY r.averageRating DESC LIMIT 10''', conn)
    sns.barplot(data=df, x='averageRating', y='primaryTitle', orient='h')
    plt.title('Top 10 Highest Rated Movies (min 1000 votes)')
    plt.xlabel('Average Rating')
    plt.ylabel('Movie Title')
    plt.show()

def plot_movies_by_periods_together(conn):
    periods = [
        (1800, 1900),
        (1900, 2000),
        (2000, 2010),
        (2010, 2025)
    ]
    period_labels = [f"{start}-{end-1}" for start, end in periods]
    counts = []
    for start, end in periods:
        df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM title_basics WHERE titleType = 'movie' AND startYear >= '{start}' AND startYear < '{end}' AND startYear != '\\N'", conn)
        counts.append(df['count'].iloc[0])
    plt.figure(figsize=(8, 5))
    sns.barplot(x=period_labels, y=counts, palette='viridis')
    plt.title('Number of Movies Released by Period')
    plt.xlabel('Period')
    plt.ylabel('Number of Movies')
    plt.tight_layout()
    plt.show()

def plot_movies_by_periods_hist(conn):
    periods = [
        (1800, 1900),
        (1900, 2000),
        (2000, 2010),
        (2010, 2025)
    ]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    plt.figure(figsize=(10, 6))
    for (start, end), color in zip(periods, colors):
        df = pd.read_sql_query(f"SELECT startYear FROM title_basics WHERE titleType = 'movie' AND startYear >= '{start}' AND startYear < '{end}' AND startYear != '\\N'", conn)
        df['startYear'] = pd.to_numeric(df['startYear'], errors='coerce')
        sns.histplot(df['startYear'], bins=10, color=color, label=f'{start}-{end-1}', kde=False, element='step', stat='count', alpha=0.7)
    plt.title('Movies Released by Periods (Overlayed)')
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.legend(title='Period')
    plt.tight_layout()
    plt.show()

def load_config(config_path='dataset_config.json'):
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def get_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [row[0] for row in cur.fetchall()]

def get_columns(conn, table):
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info({table})')
    return [row[1] for row in cur.fetchall()]

def select_table_and_column(conn):
    tables = get_tables(conn)
    print("Available tables:")
    for i, t in enumerate(tables):
        print(f"{i+1}. {t}")
    t_idx = int(input("Select a table by number: ")) - 1
    table = tables[t_idx]
    columns = get_columns(conn, table)
    print(f"Available columns in {table}:")
    for i, c in enumerate(columns):
        print(f"{i+1}. {c}")
    c_idx = int(input("Select a column by number: ")) - 1
    column = columns[c_idx]
    return table, column

def plot_column_hist(conn, table, column):
    try:
        df = pd.read_sql_query(f'SELECT {column} FROM {table}', conn)
        if df[column].dtype == object:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        sns.histplot(df[column].dropna(), bins=20)
        plt.title(f'Distribution of {column} in {table}')
        plt.xlabel(column)
        plt.ylabel('Count')
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error plotting {column} from {table}: {e}")

def get_connection():
    parser = argparse.ArgumentParser(description='IMDB Data Visualization Tool (Scalable)')
    parser.add_argument('--db', type=str, default='data/imdb_db.sqlite', help='Path to SQLite database file')
    args = parser.parse_args()
    if not os.path.exists(args.db):
        raise FileNotFoundError(f"Database file not found: {args.db}")
    return sqlite3.connect(args.db)

def plot_budget_distribution(df):
    sns.histplot(df['budget'][df['budget'] > 0], bins=30)
    plt.title('Distribution of Movie Budgets')
    plt.xlabel('Budget')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

def plot_revenue_distribution(df):
    sns.histplot(df['revenue'][df['revenue'] > 0], bins=30)
    plt.title('Distribution of Movie Revenues')
    plt.xlabel('Revenue')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

def plot_runtime_distribution(df):
    sns.histplot(df['runtime'].dropna(), bins=30)
    plt.title('Distribution of Movie Runtimes')
    plt.xlabel('Runtime (minutes)')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

def plot_top_genres(df):
    import ast
    genres = df['genres'].dropna().apply(lambda x: [g['name'] for g in ast.literal_eval(x)])
    from collections import Counter
    genre_list = [g for sublist in genres for g in sublist]
    genre_counts = Counter(genre_list)
    genre_df = pd.DataFrame(genre_counts.items(), columns=['Genre', 'Count']).sort_values('Count', ascending=False)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=genre_df, x='Genre', y='Count', palette='viridis')
    plt.title('Top Genres')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def plot_avg_rating_by_genre(df):
    import ast
    rows = []
    for _, row in df.iterrows():
        if pd.notnull(row['genres']):
            for genre in ast.literal_eval(row['genres']):
                rows.append({'Genre': genre['name'], 'Rating': row['vote_average']})
    genre_df = pd.DataFrame(rows)
    avg_df = genre_df.groupby('Genre')['Rating'].mean().reset_index().sort_values('Rating', ascending=False)
    sns.barplot(data=avg_df, x='Genre', y='Rating')
    plt.title('Average Movie Rating by Genre')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_movies_per_year(df):
    df['year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
    sns.histplot(df['year'].dropna(), bins=30)
    plt.title('Number of Movies Released per Year')
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

def plot_top10_by_vote_count(df):
    top10 = df.sort_values('vote_count', ascending=False).head(10)
    sns.barplot(data=top10, x='vote_count', y='title', orient='h')
    plt.title('Top 10 Movies by Vote Count')
    plt.xlabel('Vote Count')
    plt.ylabel('Movie Title')
    plt.tight_layout()
    plt.show()

def plot_popularity_distribution(df):
    sns.histplot(df['popularity'].dropna(), bins=30)
    plt.title('Distribution of Movie Popularity')
    plt.xlabel('Popularity')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    df = pd.read_csv('data/tmdb_5000_movies.csv')
    while True:
        choice = menu()
        if choice == '1':
            plot_budget_distribution(df)
        elif choice == '2':
            plot_revenue_distribution(df)
        elif choice == '3':
            plot_runtime_distribution(df)
        elif choice == '4':
            plot_top_genres(df)
        elif choice == '5':
            plot_avg_rating_by_genre(df)
        elif choice == '6':
            plot_movies_per_year(df)
        elif choice == '7':
            plot_top10_by_vote_count(df)
        elif choice == '8':
            plot_popularity_distribution(df)
        elif choice == '0':
            print("Exiting TMDB Visualization Menu.")
            break
        else:
            print("Invalid option. Please try again.")
