"""
Configuration management for Retail Insights Assistant
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str = None) -> Optional[str]:
    """Get secret from Streamlit secrets or environment - called dynamically"""
    # First check environment variables
    env_val = os.getenv(key)
    if env_val:
        return env_val
    
    # Then try Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    
    return default


class Settings(BaseSettings):
    """Application settings"""
    
    # LLM Configuration - Default to Google Gemini for Streamlit Cloud
    llm_provider: str = os.getenv("LLM_PROVIDER", "google")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Application Settings
    data_path: str = os.getenv("DATA_PATH", "./data/sales_data.csv")
    max_context_length: int = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.1"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Database Configuration - Use in-memory for Streamlit Cloud
    duckdb_path: str = os.getenv("DUCKDB_PATH", ":memory:")
    
    # Agent Configuration
    enable_logging: bool = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
