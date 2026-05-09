import mysql.connector
import pandas as pd
from datetime import datetime

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'finance_sentiment'
}

def init_db():
    """Creates the table if it doesn't exist."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            ticker VARCHAR(10),
            score FLOAT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def save_to_db(ticker, score):
    """Inserts a new sentiment record into MySQL."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO sentiment_history (timestamp, ticker, score) VALUES (%s, %s, %s)"
        values = (datetime.now(), ticker, round(float(score), 4))
        
        cursor.execute(query, values)
        conn.commit()
        print(f"✅ MySQL: Saved {ticker}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ MySQL Error: {e}")

def load_history(ticker):
    """Queries history for a specific ticker and returns a DataFrame."""
    try:
        conn = mysql.connector.connect(**db_config)
        query = "SELECT timestamp, ticker, score FROM sentiment_history WHERE ticker = %s ORDER BY timestamp ASC"
        
        # Pandas can read directly from a SQL query
        df = pd.read_sql(query, conn, params=(ticker,))
        
        conn.close()
        return df
    except Exception as e:
        print(f"❌ MySQL Load Error: {e}")
        return pd.DataFrame()