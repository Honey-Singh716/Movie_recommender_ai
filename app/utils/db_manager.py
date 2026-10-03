import sqlite3
import pandas as pd
import json
import os
import streamlit as st

_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROJECT_ROOT = os.path.dirname(_APP_DIR)
DB_PATH = os.path.join(_PROJECT_ROOT, "data", "movies.db")
DATA_DIR = os.path.join(_PROJECT_ROOT, "data", "processed")
MODELS_DIR = os.path.join(_PROJECT_ROOT, "models")

def get_connection():
    """Return a SQLite connection with WAL mode and timeout for concurrent access safety."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    """Initialize SQLite database and populate tables from pickle/CSV if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if movies table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movies';")
    exists = cursor.fetchone()
    
    if not exists:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # Load cleaned movie data
        pkl_path = os.path.join(MODELS_DIR, 'cleaned_movie_data.pkl')
        if os.path.exists(pkl_path):
            df = pd.read_pickle(pkl_path)
            
            # Serialize list/dict columns to JSON strings
            list_cols = ['genres', 'keywords', 'cast', 'crew', 'production_companies', 'production_countries', 'spoken_languages']
            for col in list_cols:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
            
            # Write to SQLite
            df.to_sql('movies', conn, if_exists='replace', index=False)
        
        # Load cast_df.csv
        cast_csv_path = os.path.join(DATA_DIR, 'cast_df.csv')
        if os.path.exists(cast_csv_path):
            cast_df = pd.read_csv(cast_csv_path)
            cast_df.to_sql('cast', conn, if_exists='replace', index=False)
            
        # Create indexes for fast search
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_title ON movies (title);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_id ON movies (id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cast_movie_id ON cast (movie_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cast_name ON cast (name);")
        conn.commit()
    conn.close()

def load_all_movies():
    """Load all movies as a pandas DataFrame, deserializing JSON columns."""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()
    
    # Deserialize list columns
    list_cols = ['genres', 'keywords', 'cast', 'crew', 'production_companies', 'production_countries', 'spoken_languages']
    for col in list_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: json.loads(x) if isinstance(x, str) and x.startswith(('[', '{')) else x)
    return df

def load_cast_data():
    """Load cast data as a DataFrame."""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM cast", conn)
    conn.close()
    return df

def get_movie_by_title(title):
    """Retrieve a single movie by title."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE title = ?", (title,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    # Fetch column names
    col_names = [description[0] for description in cursor.description]
    movie = dict(zip(col_names, row))
    conn.close()
    
    # Deserialize list columns
    list_cols = ['genres', 'keywords', 'cast', 'crew', 'production_companies', 'production_countries', 'spoken_languages']
    for col in list_cols:
        if col in movie and isinstance(movie[col], str) and movie[col].startswith(('[', '{')):
            try:
                movie[col] = json.loads(movie[col])
            except Exception:
                pass
    return movie

def search_movies_in_db(query, limit=15):
    """Search movies matching query title or original title."""
    if not query:
        return []
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title FROM movies WHERE title LIKE ? OR original_title LIKE ? ORDER BY popularity DESC LIMIT ?",
        (f"%{query}%", f"%{query}%", limit)
    )
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def insert_movie_to_db(movie_dict, cast_list):
    """Insert or replace a movie and its cast in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Serialize lists to JSON string
    list_cols = ['genres', 'keywords', 'cast', 'crew', 'production_companies', 'production_countries', 'spoken_languages']
    for col in list_cols:
        if col in movie_dict and isinstance(movie_dict[col], (list, dict)):
            movie_dict[col] = json.dumps(movie_dict[col])
            
    # Prepare SQL for movie
    columns = ', '.join(movie_dict.keys())
    placeholders = ', '.join('?' for _ in movie_dict)
    sql = f"INSERT OR REPLACE INTO movies ({columns}) VALUES ({placeholders})"
    
    try:
        cursor.execute(sql, list(movie_dict.values()))
        
        # Insert cast
        for actor in cast_list:
            cols = ', '.join(actor.keys())
            pl = ', '.join('?' for _ in actor)
            cast_sql = f"INSERT OR REPLACE INTO cast ({cols}) VALUES ({pl})"
            cursor.execute(cast_sql, list(actor.values()))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_db_stats():
    """Return quick statistics about the database for display."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM movies")
        total_movies = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT name) FROM cast")
        total_actors = cursor.fetchone()[0]
        conn.close()
        return {"total_movies": total_movies, "total_actors": total_actors}
    except Exception:
        return {"total_movies": 0, "total_actors": 0}
