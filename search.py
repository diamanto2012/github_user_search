import requests
import time
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
import argparse

# Определяем базу данных и модель
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


def fetch_github_users(query):
    users = []
    page = 1
    while True:
        url = f"https://api.github.com/search/users?q={query}&per_page=100&page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Генерирует исключение для HTTP ошибок

            # Проверяем лимиты API
            remaining_requests = int(response.headers.get('X-RateLimit-Remaining', 0))
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))

            if remaining_requests == 0:
                wait_time = reset_time - int(time.time())
                if wait_time > 0:
                    print(f"Достигнут лимит запросов. Ожидание {wait_time} секунд до сброса лимита.")
                    time.sleep(wait_time)  # Ждем сброса лимита

            data = response.json()

            # Проверяем наличие пользователей в ответе
            if 'items' in data and data['items']:
                users.extend(data['items'])
                print(f"Получены пользователи с страницы {page}: {len(data['items'])} пользователей.")
                page += 1
            else:
                print("Достигнута последняя страница или нет пользователей.")
                break  # Выход из цикла, если нет пользователей или достигнута последняя страница

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            break  # Выход из цикла при ошибке запроса

    return users


def save_users_to_db(users):
    session = Session()  # Создаем новую сессию для работы с БД
    new_users_count = 0  # Счетчик новых пользователей
    try:
        for user in users:
            github_user = User(username=user['login'], url=user['html_url'])
            # Проверяем, существует ли уже пользователь в базе данных
            if session.query(User).filter_by(username=user['login']).first() is None:
                session.add(github_user)
                new_users_count += 1
        session.commit()
        print(f"Добавлено {new_users_count} новых пользователей в базу данных.")
    except Exception as e:
        print(f"Ошибка при сохранении пользователей в базу данных: {e}")
        session.rollback()  # Откат изменений в случае ошибки
    finally:
        session.close()  # Закрываем сессию


def main(query):
    users = fetch_github_users(query)
    if users:  # Проверяем, есть ли пользователи для сохранения
        save_users_to_db(users)

    # Получаем общее количество пользователей в базе данных после сохранения новых
    session = Session()
    total_users_count = session.query(User).count()
    session.close()

    print(f"Общее количество пользователей в базе данных: {total_users_count}")


if __name__ == "__main__":
    # Настройка аргументов командной строки
    parser = argparse.ArgumentParser(description='Поиск пользователей GitHub по запросу.')
    parser.add_argument('query', type=str, help='Поисковый запрос (например, "octocat")')

    args = parser.parse_args()

    main(args.query)