from sqlalchemy import create_engine
from models.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Set to False to not trigger a database reset. True will initiate a drop and creation of the database.
RESET_DB = True

db_url = os.getenv("DB_URL")
engine = create_engine(db_url, echo=True)

# Reset the database setup by dropping all tables and creating them
if RESET_DB:
    try:
        Base.metadata.drop_all(engine)
        print("Database dropped")
        Base.metadata.create_all(engine)
        print("Database has been created")
    except Exception as e:
        print(f"An error has occurred: {e}")
