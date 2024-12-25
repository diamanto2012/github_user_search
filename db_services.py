import requests
import time
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import argparse

# Определяем базу данных и модель
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    url = Column(String)
    avatar_url = Column(String)
    node_id = Column(String)
    gravatar_id = Column(String)
    followers_url = Column(String)
    following_url = Column(String)
    gists_url = Column(String)
    starred_url = Column(String)
    subscriptions_url = Column(String)
    organizations_url = Column(String)
    repos_url = Column(String)
    events_url = Column(String)
    received_events_url = Column(String)
    user_type = Column(
        String
    )  # Изменено с 'type' на 'user_type', чтобы избежать конфликта с ключевым словом
    user_view_type = Column(String)
    site_admin = Column(Boolean)
    score = Column(Float)
