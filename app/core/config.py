from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL")
    embedding_model: str = os.getenv("EMBEDDING_MODEL")
    question_index_name: str = os.getenv("QUESTION_INDEX_NAME")
    chunk_index_name: str = os.getenv("CHUNK_INDEX_NAME")

settings = Settings()
