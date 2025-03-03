from sqlalchemy import create_engine
import pandas as pd
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

class DatabaseManager:
    def __init__(self):
        self.connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        self.engine = create_engine(self.connection_string)

    def execute_query(self, query):
        try:
            
            df = pd.read_sql_query(query, self.engine)
            
            
            date_columns = df.select_dtypes(include=['datetime64']).columns
            for col in date_columns:
                df[col] = pd.to_datetime(df[col]).dt.tz_localize(None)
            
            return df
                
        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}")

    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            raise Exception(f"Connection test failed: {str(e)}") 