# IDBM Movie Data Analysis & Visualization


This project provides tools for interacting with and analyzing movie data from IMDB and TMDB. It includes a command-line interface for data management using SQLite and powerful visualizations using matplotlib and seaborn.

# 📁 Project Structure
imdb_analysis.py: CLI tool to import CSVs into SQLite and perform CRUD operations on the database.

visualize_imdb.py: Interactive visualization tool for movie data from both IMDB and TMDB datasets.

data/: Directory to store your SQLite database and CSV files.

# 🔧 Features
imdb_analysis.py
CSV Import to SQLite: Load movie metadata from CSVs into a SQLite database.

Interactive CRUD Menu:

Create: Insert new rows into tables

Read: View existing rows (limited to 10 for preview)

Update: Modify specific entries

Delete: Remove entries by filter condition

visualize_imdb.py
Visualizations on IMDB Ratings Data:

Movie Ratings Distribution

Genre-wise Rating Averages

Number of Movies per Year

Top-Rated Movies

Genre Distribution

Visualizations on TMDB 5000 Movies Dataset:

Budget and Revenue Distribution

Runtime and Popularity Histograms

Genre Count and Average Rating by Genre

Top 10 Movies by Vote Count

Custom Column Plots: Select any table and column to plot a histogram.

# 🚀 Getting Started
Prerequisites
Ensure you have the following installed:

Python 3.7+

pip

Install required Python libraries:

bash
Copy
Edit
pip install pandas matplotlib seaborn
Dataset
Place your SQLite DB and CSV files in a folder named data/.

Example:

data/imdb_db.sqlite

data/tmdb_5000_movies.csv

# 🛠 Usage
1. IMDB Data Manager
bash
Copy
Edit
python imdb_analysis.py --db data/imdb_db.sqlite
Options include:

Import CSV into database

Perform CRUD operations on tables

2. Visualization Dashboard
bash
Copy
Edit
python visualize_imdb.py --db data/imdb_db.sqlite
Select an option from the menu to view various visualizations for IMDB datasets.

# 📊 Sample Visuals
Rating distribution histograms

Bar plots for top genres

Movie release trends over time

Top-rated movies by average rating and vote count

# 📌 Notes
Some genre data may need cleaning depending on your CSV format.

Ensure columns like startYear, genres, vote_average, popularity, and revenue are well-formatted.

For TMDB visualizations, ensure the file tmdb_5000_movies.csv is present under data/.

 # 📃 License
This project is open-source and free to use under the MIT License.
