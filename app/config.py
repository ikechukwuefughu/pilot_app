import os

class Config:
    # Flask security key
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Database connection (Azure SQL)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
