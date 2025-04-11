import os
import sqlite3
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def init_db(db_path='recruitment.db'):
    """Initialize the SQLite database with the schema"""
    try:
        # Ensure the database directory exists
        db_dir = Path(db_path).parent
        if db_dir.name:  # If there's a directory part
            db_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to the database
        logger.info(f"Initializing database at {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read schema from file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(current_dir, 'schema.sql')
        
        with open(schema_path, 'r') as f:
            schema_script = f.read()
        
        # Execute schema script
        cursor.executescript(schema_script)
        conn.commit()
        
        logger.info("Database initialized successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # If run directly, initialize the database
    init_db()
