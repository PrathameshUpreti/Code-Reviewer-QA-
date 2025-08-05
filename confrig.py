import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Platform configuration settings."""
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./outputs")
    ENABLE_HUMAN_FEEDBACK: bool = os.getenv("ENABLE_HUMAN_FEEDBACK", "true").lower() == "true"
    MAX_TURNS: int = int(os.getenv("MAX_TURNS", 20))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.3))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 4000))
    @classmethod
    def get_api_key(cls) -> str:
        """Get available API key (prioritize OpenRouter for free usage)."""
        if cls.OPENROUTER_API_KEY:
            return cls.OPENROUTER_API_KEY
        elif cls.OPENAI_API_KEY:
            return cls.OPENAI_API_KEY
        else:
            raise ValueError("No API key found. Please set OPENROUTER_API_KEY or OPENAI_API_KEY")
    
    @classmethod
    def get_base_url(cls) -> Optional[str]:
        """Get base URL for API calls."""
        if cls.OPENROUTER_API_KEY:
            return cls.OPENROUTER_BASE_URL
        return None  # Use default OpenAI endpoint

    @classmethod
    def use_openrouter(cls):
        return bool(cls.OPENROUTER_API_KEY) # Use OpenRouter if API key is set
    
    @classmethod
    def get_model(cls) -> str:
        """Get model name."""
        if cls.OPENROUTER_API_KEY:
            return cls.DEFAULT_MODEL
        return "gpt-4"  # Default OpenAI model