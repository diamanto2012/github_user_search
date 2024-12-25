import argparse
from services import GitHubUserFetcher

def main(query):
    fetcher = GitHubUserFetcher()
    users = fetcher.fetch_github_users(query)
    if users:  # Проверяем, есть ли пользователи для сохранения
        fetcher.save_users_to_db(users)

    total_users_count = fetcher.get_total_users_count()
    print(f"Общее количество пользователей в базе данных: {total_users_count}")

if __name__ == "__main__":
    # Настройка аргументов командной строки
    parser = argparse.ArgumentParser(description='Поиск пользователей GitHub по запросу.')
    parser.add_argument('query', type=str, help='Поисковый запрос (например, "octocat")')

    args = parser.parse_args()

    main(args.query)