import sqlite3
import csv
import os
import argparse
import pandas as pd
from pick import pick

def create_connection(db_path):
    conn = sqlite3.connect(db_path)
    return conn

def import_csv_to_sqlite(db_path, csv_path, table_name, if_exists='replace'):
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    conn.close()
    print(f"Imported {csv_path} to table '{table_name}' in {db_path}")

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
        print("2. Read (Query Table)")
        print("3. Update Row")
        print("4. Delete Row")
        print("0. Back to Main Menu")
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
            table = input("Enter table name: ")
            try:
                df = pd.read_sql_query(f'SELECT * FROM {table} LIMIT 10', conn)
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
    args = parser.parse_args()
    conn = create_connection(args.db)
    while True:
        print("\nIMDB Data Management Menu:")
        print("1. Import CSV to SQLite Table")
        print("2. CRUD Operations")
        print("0. Exit")
        choice = input("Select an option: ")
        if choice == '1':
            # Check for existing CSV files in data folder
            data_dir = os.path.dirname(args.db)
            if not data_dir:  # If args.db doesn't contain a directory path
                data_dir = 'data'
            
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            
            if csv_files:
                try:
                    options = csv_files + ["Enter another path"]
                    title = 'Select a CSV file (use arrow keys and Enter to select):'
                    selected, index = pick(options, title)
                    
                    if selected == "Enter another path":
                        csv_path = input("Enter CSV file path: ")
                    else:
                        csv_path = os.path.join(data_dir, selected)
                except ImportError:
                    print("\nThe 'pick' library is not installed. Using fallback selection method.")
                    print("\nExisting CSV files in data folder:")
                    for i, file in enumerate(csv_files, 1):
                        print(f"{i}. {file}")
                    print(f"{len(csv_files) + 1}. Enter another path")
                    
                    file_choice = input("\nSelect a file or enter another path (number): ")
                    try:
                        file_idx = int(file_choice) - 1
                        if 0 <= file_idx < len(csv_files):
                            csv_path = os.path.join(data_dir, csv_files[file_idx])
                        else:
                            csv_path = input("Enter CSV file path: ")
                    except ValueError:
                        csv_path = input("Enter CSV file path: ")
            else:
                print("No CSV files found in data directory.")
                csv_path = input("Enter CSV file path: ")
            
            table_name = input("Enter table name for SQLite: ")
            import_csv_to_sqlite(args.db, csv_path, table_name)
        elif choice == '2':
            crud_menu(conn)
        elif choice == '0':
            print("Exiting IMDB Data Management Menu.")
            break
        else:
            print("Invalid option. Please try again.")
    conn.close()

if __name__ == '__main__':
    main()
