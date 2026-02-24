# from pydantic_settings import BaseSettings
# import os

# ENV = os.getenv('ENV', 'development')

# print(f"Cargando ambiente: {ENV}")
# print(f"Archivo env: .env.{ENV}")

# class Settings(BaseSettings):
#     POSTGRES_USER: str
#     POSTGRES_PASSWORD: str
#     POSTGRES_DB: str
#     DATABASE_URL: str

#     class Config:
#         env_file = f".env.{os.getenv('ENV', 'development')}"

# settings = Settings()


from pydantic_settings import BaseSettings
import os

ENV = os.getenv('ENV', 'development')

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    class Config:
        env_file = f".env.{os.getenv('ENV', 'development')}"
        env_file_encoding = "utf-8"

settings = Settings()