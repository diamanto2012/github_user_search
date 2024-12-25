import requests
import sqlite3
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

# Определяем базу данных> и модель
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    url = Column(String)


# Подключение к базе данных SQLite
engine = create_engine('sqlite:///github_users.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def fetch_github_users(query):
    users = []
    page = 1
    while True:
        url = f"https://api.github.com/search/users?q={query}&per_page=100&page={page}"
        response = requests.get(url)
        data = response.json()

        # Проверяем наличие пользователей в ответе
        if 'items' in data and data['items']:
            users.extend(data['items'])
            print(f"Получены пользователи с страницы {page}")
            page += 1
        else:
            break  # Выход из цикла, если нет пользователей или достигнута последняя страница
    return users


def save_users_to_db(users):
    for user in users:
        github_user = User(username=user['login'], url=user['html_url'])
        # Проверяем, существует ли уже пользователь в базе данных
        if session.query(User).filter_by(username=user['login']).first() is None:
            session.add(github_user)
    session.commit()


def main():
    query = input("Введите поисковый запрос (например, 'octocat'): ")
    users = fetch_github_users(query)
    save_users_to_db(users)
    print(f"Сохранено {len(users)} пользователей в базе данных.")


if __name__ == "__main__":
    main()
    session.close()