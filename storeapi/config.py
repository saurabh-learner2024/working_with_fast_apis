from typing import Optional
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# Base configuration class that loads environment variables from a .env file
class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None  # Environment state (dev, prod, test)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Global configuration class inheriting from BaseConfig
class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None  # Database connection URL
    DB_FORCE_ROLL_BACK: bool = False  # Flag for rolling back database transactions
    LOGTAIL_API_KEY : Optional[str] = None


# Development configuration class inheriting from GlobalConfig
class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")  # Prefix for development environment variables


# Production configuration class inheriting from GlobalConfig
class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")  # Prefix for production environment variables


# Test configuration class inheriting from GlobalConfig
class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///test1.db"  # Default database URL for testing
    DB_FORCE_ROLL_BACK: bool = True  # Enable rollbacks for testing environment
    model_config = SettingsConfigDict(env_prefix="TEST_")  # Prefix for testing environment variables


# Function to get the appropriate configuration based on the environment state
@lru_cache()
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


# Load the configuration based on the ENV_STATE environment variable
config = get_config(BaseConfig().ENV_STATE)
