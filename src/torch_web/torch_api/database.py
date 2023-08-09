import os
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv


load_dotenv()
engine = create_engine(os.environ.get("TORCH_HUB_DATABASE_URI"))

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)