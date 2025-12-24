"""
Configuration management for Retail Insights Assistant
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # LLM Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # Application Settings
    data_path: str = os.getenv("DATA_PATH", "./data/sales_data.csv")
    max_context_length: int = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.1"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Database Configuration
    duckdb_path: str = os.getenv("DUCKDB_PATH", "./data/retail_insights.duckdb")
    
    # Agent Configuration
    enable_logging: bool = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
