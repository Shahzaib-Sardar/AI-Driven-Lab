import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
    JSON_SORT_KEYS = False
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
