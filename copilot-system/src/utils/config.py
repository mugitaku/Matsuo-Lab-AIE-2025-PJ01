import os
from typing import Optional
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Model Configuration
    model_name: str = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Vector Store Configuration
    vector_store_type: str = os.getenv("VECTOR_STORE_TYPE", "chroma")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Application Settings
    app_port: int = int(os.getenv("APP_PORT", "8501"))
    debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Paths
    data_dir: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    exercises_dir: str = os.path.join(data_dir, "exercises")
    vector_store_path: str = os.path.join(data_dir, "vector_store")
    
    class Config:
        env_file = ".env"


settings = Settings()