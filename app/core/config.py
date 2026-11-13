from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-LMS API"
    API_V1_STR: str = "/api/v1"
    
    # Database configurations
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "lms_user"
    POSTGRES_PASSWORD: str = "lms_password"
    POSTGRES_DB: str = "lms_db"
    POSTGRES_PORT: str = "5432"
    
    # Construct the async connection string
    @property
    def ASYNC_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
    # Security
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_CHANGE_THIS_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Redis / Celery
    REDIS_URI: str = "redis://localhost:6379/0"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
