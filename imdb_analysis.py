import sqlite3
import csv
import os
import argparse
import pandas as pd
import json

def create_connection(db_path):
    conn = sqlite3.connect(db_path)
    return conn

def clean_genres(genres_str):
    try:
        genres = json.loads(genres_str.replace("'", '"'))
        return ', '.join([g['name'] for g in genres])
    except Exception:
        return ''

def clean_cast(cast_str, n=3):
    try:
        cast = json.loads(cast_str.replace("'", '"'))
        return ', '.join([c['name'] for c in cast[:n]])
    except Exception:
        return ''

def clean_crew(crew_str, job='Director'):
    try:
        crew = json.loads(crew_str.replace("'", '"'))
        names = [c['name'] for c in crew if c.get('job') == job]
        return ', '.join(names)
    except Exception:
        return ''

def import_and_clean_movies(db_path, csv_path, table_name='movies'):
    df = pd.read_csv(csv_path)
    # Clean genres
    df['genres'] = df['genres'].apply(clean_genres)
    # Keep only useful columns
    useful_cols = ['id', 'title', 'genres', 'release_date', 'popularity', 'vote_average', 'vote_count', 'runtime', 'budget', 'revenue']
    df = df[useful_cols]
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Imported and cleaned {csv_path} to table '{table_name}' in {db_path}")

def import_and_clean_credits(db_path, csv_path, table_name='credits'):
    df = pd.read_csv(csv_path)
    # Clean cast and crew
    df['main_cast'] = df['cast'].apply(lambda x: clean_cast(x, n=3))
    df['director'] = df['crew'].apply(clean_crew)
    # Keep only useful columns
    useful_cols = ['movie_id', 'title', 'main_cast', 'director']
    df = df[useful_cols]
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Imported and cleaned {csv_path} to table '{table_name}' in {db_path}")

def get_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [row[0] for row in cur.fetchall()]

def get_columns(conn, table):
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info({table})')
    return [row[1] for row in cur.fetchall()]

def crud_menu(conn):
    while True:
        print("\nCRUD Menu:")
        print("1. Create (Insert Row)")
        print("2. Read (Run SQL Query)")
        print("3. Update Row")
        print("4. Delete Row")
        print("0. Exit")
        choice = input("Select an option: ")
        if choice == '1':
            table = input("Enter table name: ")
            columns = get_columns(conn, table)
            values = []
            for col in columns:
                values.append(input(f"Enter value for {col}: "))
            placeholders = ','.join(['?'] * len(columns))
            sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            try:
                cur = conn.cursor()
                cur.execute(sql, values)
                conn.commit()
                print("Row inserted.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '2':
            print("Enter your SQL query (end with an empty line):")
            lines = []
            while True:
                line = input()
                if line.strip() == '':
                    break
                lines.append(line)
            query = '\n'.join(lines)
            try:
                df = pd.read_sql_query(query, conn)
                print(df)
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '3':
            table = input("Enter table name: ")
            columns = get_columns(conn, table)
            set_col = input(f"Which column to update? {columns}: ")
            set_val = input(f"New value for {set_col}: ")
            where_col = input(f"Which column to filter by? {columns}: ")
            where_val = input(f"Value for {where_col}: ")
            sql = f"UPDATE {table} SET {set_col} = ? WHERE {where_col} = ?"
            try:
                cur = conn.cursor()
                cur.execute(sql, (set_val, where_val))
                conn.commit()
                print("Row(s) updated.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '4':
            table = input("Enter table name: ")
            columns = get_columns(conn, table)
            where_col = input(f"Which column to filter by? {columns}: ")
            where_val = input(f"Value for {where_col}: ")
            sql = f"DELETE FROM {table} WHERE {where_col} = ?"
            try:
                cur = conn.cursor()
                cur.execute(sql, (where_val,))
                conn.commit()
                print("Row(s) deleted.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '0':
            break
        else:
            print("Invalid option. Please try again.")

def main():
    parser = argparse.ArgumentParser(description='IMDB Data Management Tool')
    parser.add_argument('--db', type=str, default='data/imdb_db.sqlite', help='Path to SQLite database file')
    parser.add_argument('--movies', type=str, default='data/tmdb_5000_movies.csv', help='Path to movies CSV')
    parser.add_argument('--credits', type=str, default='data/tmdb_5000_credits.csv', help='Path to credits CSV')
    args = parser.parse_args()
    # Auto-import and clean both CSVs
    import_and_clean_movies(args.db, args.movies)
    import_and_clean_credits(args.db, args.credits)
    conn = create_connection(args.db)
    while True:
        print("\nIMDB Data Management Menu:")
        print("1. CRUD Operations")
        print("0. Exit")
        choice = input("Select an option: ")
        if choice == '1':
            crud_menu(conn)
        elif choice_str == "Exit":
            try:
                confirm = subprocess.run(
                    ['gum', 'confirm', '--selected.background=212', '--selected.foreground=0', '--affirmative', 'Yes', '--negative', 'No', 'Are you Sure ?'],
                    text=True
                )
                if confirm.returncode != 0:
                    print("Exit cancelled.")
                    continue
            except Exception:
                ans = input("Are you sure you want to exit? (y/n): ")
                if ans.lower() not in ('y', 'yes'):
                    print("Exit cancelled.")
                    continue
            print("Exiting IMDB Data Management Menu.")
            break
        else:
            print("Invalid option. Please try again.")
    conn.close()

if __name__ == '__main__':
    main()
