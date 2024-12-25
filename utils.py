import argparse

from db_services import GitHubUserFetcher


def run_github_fetcher(query: str):
    try:
        github_fetcher = GitHubUserFetcher()
    except Exception as e:
        print(f"Ошибка при инициализации GitHubUserFetcher: {e}")
        return  # Завершаем выполнение функции в случае ошибки

    try:
        users = github_fetcher.fetch_github_users(query)
        if users:  # Проверяем, есть ли пользователи для сохранения
            github_fetcher.save_users_to_db(users)

        total_users_count = github_fetcher.get_total_users_count()
        print(f"Общее количество пользователей в базе данных: {total_users_count}")
    except Exception as e:
        print(f"Ошибка во время выполнения основной логики: {e}")


def get_command_line_arguments():
    # Настройка аргументов командной строки
    argument_command_line_parser = argparse.ArgumentParser(
        description="Поиск пользователей GitHub по запросу."
    )
    argument_command_line_parser.add_argument(
        "query",
        help='Поисковый запрос (например, "python django react native backend")',
    )
    args = argument_command_line_parser.parse_args()
    return args
