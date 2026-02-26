import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# override=True ensures it picks up the clean .env file over messed up shell variables
load_dotenv(override=True)

def test_connection():
    db_url = os.environ.get("DATABASE_URL", "").replace("DATABASE_URL=", "").strip("'\"")
    
    if not db_url:
        print("DATABASE_URL not found.")
        return
        
    engine = create_engine(
        db_url,
        pool_pre_ping=True, 
        connect_args={"connect_timeout": 10}
    )
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print("✓ Connection successful!")
            print(f"Database version: {result.scalar()}")
    except Exception as e:
        print("❌ Connection failed:")
        print(e)

if __name__ == "__main__":
    test_connection()