import time

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_service import User, Base
from exceptions import GitHubUserParserException


def fetch_github_users(query):
    users = []
    page = 1
    while True:
        url = f"https://api.github.com/search/users?q={query}&per_page=100&page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Генерирует исключение для HTTP ошибок

            # Проверяем лимиты API
            remaining_requests = int(response.headers.get("X-RateLimit-Remaining", 0))
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))

            if remaining_requests == 0:
                wait_time = reset_time - int(time.time())
                if wait_time > 0:
                    print(
                        f"Достигнут лимит запросов. Ожидание {wait_time} секунд до сброса лимита."
                    )
                    time.sleep(wait_time)  # Ждем сброса лимита

            data = response.json()

            # Проверяем наличие пользователей в ответе
            if "items" in data and data["items"]:
                users.extend(data["items"])
                print(
                    f"Получены пользователи с страницы {page}: {len(data['items'])} пользователей."
                )
                page += 1
            else:
                print("Достигнута последняя страница или нет пользователей.")
                break  # Выход из цикла, если нет пользователей или достигнута последняя страница

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            break  # Выход из цикла при ошибке запроса

    return users


class GitHubUserParser:
    def __init__(self, db_url="sqlite:///github_users.db"):
        # Подключение к базе данных SQLite
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_users_to_db(self, users):
        new_users_count = 0  # Счетчик новых пользователей
        with self.Session() as session:  # Используем контекстный менеджер для сессии
            try:
                for user in users:
                    github_user = User(
                        username=user["login"],
                        url=user["html_url"],
                        avatar_url=user["avatar_url"],
                        node_id=user["node_id"],
                        gravatar_id=user.get(
                            "gravatar_id", ""
                        ),  # Используем get для безопасного доступа
                        followers_url=user["followers_url"],
                        following_url=user["following_url"],
                        gists_url=user["gists_url"],
                        starred_url=user["starred_url"],
                        subscriptions_url=user["subscriptions_url"],
                        organizations_url=user["organizations_url"],
                        repos_url=user["repos_url"],
                        events_url=user["events_url"],
                        received_events_url=user["received_events_url"],
                        user_type=user["type"],  # Переименовано на user_type
                        user_view_type=user.get(
                            "user_view_type", ""
                        ),  # Используем get для безопасного доступа
                        site_admin=user.get(
                            "site_admin", False
                        ),  # Используем get для безопасного доступа
                        score=user.get(
                            "score", 0.0
                        ),  # Используем get для безопасного доступа
                    )
                    # Проверяем, существует ли уже пользователь в базе данных
                    existing_user = (
                        session.query(User).filter_by(username=user["login"]).first()
                    )
                    if existing_user is None:
                        session.add(github_user)
                        new_users_count += 1
                    else:
                        print(
                            f"Пользователь {user['login']} уже существует в базе данных."
                        )
                session.commit()
                print(f"Добавлено {new_users_count} новых пользователей в базу данных.")
            except Exception as e:
                print(f"Ошибка при сохранении пользователей в базу данных: {e}")
                session.rollback()  # Откат изменений в случае ошибки

    def get_total_users_count(self):
        with self.Session() as session:  # Используем контекстный менеджер для сессии
            total_users_count = session.query(User).count()
        return total_users_count


def run_github_parser(query: str):
    try:
        github_parser = GitHubUserParser()
        users = fetch_github_users(query)
        if users:  # Проверяем, есть ли пользователи для сохранения
            github_parser.save_users_to_db(users)

        total_users_count = github_parser.get_total_users_count()
        print(f"Общее количество пользователей в базе данных: {total_users_count}")
    except Exception as e:
        raise GitHubUserParserException(
            f"Ошибка во время выполнения основной логики: {e}"
        )
