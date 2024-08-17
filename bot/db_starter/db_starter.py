import logging
import os
import sqlite3

# Путь к базе данных внутри папки 'bot'
db_path = os.path.join(os.path.dirname(__file__), '..', 'feedback_ratings.db')


def init_db():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS feedback_ratings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          )''')

        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"SQLite error occurred: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


# Ensure this function is called in your main program
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    init_db()
