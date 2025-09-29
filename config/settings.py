import os
from dataclasses import dataclass
from typing import Dict, Any
import yaml

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 3306
    username: str = "root"
    password: str = ""
    name: str = "ai_platform"
    dialect: str = "sqlite"

@dataclass
class AIConfig:
    openai_api_key: str = ""
    huggingface_token: str = ""
    local_models_path: str = "./data/models"
    default_model: str = "gpt-3.5-turbo"

@dataclass
class SocialMediaConfig:
    facebook_app_id: str = ""
    facebook_app_secret: str = ""
    instagram_access_token: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    youtube_api_key: str = ""
    tiktok_access_token: str = ""

@dataclass
class PlatformConfig:
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 5000
    secret_key: str = "your-secret-key-here"
    upload_folder: str = "./data/uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB

class Config:
    def __init__(self):
        self.database = DatabaseConfig()
        self.ai = AIConfig()
        self.social_media = SocialMediaConfig()
        self.platform = PlatformConfig()
        
        # Load from environment variables
        self._load_from_env()
        
    def _load_from_env(self):
        self.ai.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.ai.huggingface_token = os.getenv('HUGGINGFACE_TOKEN', '')
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'database': self.database.__dict__,
            'ai': self.ai.__dict__,
            'social_media': self.social_media.__dict__,
            'platform': self.platform.__dict__
        }

# Global config instance
config = Config()
