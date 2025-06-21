from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database configuration
    database_url: str = "sqlite:///./meddoc.db"
    
    # OpenAI configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo"
    
    # Embedding model configuration
    embedding_model: str = "text-embedding-3-small"
    
    # Pinecone configuration
    question_index_name: str
    chunk_index_name: str
    
    # Optional Pinecone configuration (if not using default environment)
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Create settings instance
settings = Settings()
