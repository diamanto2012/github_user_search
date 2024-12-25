import argparse

from db_services import GitHubUserParser
from exceptions import GitHubUserParserException, ArgumentCommandLineParisngException


def run_github_parser(query: str):
    try:
        github_parser = GitHubUserParser()
        users = github_parser.fetch_github_users(query)
        if users:  # Проверяем, есть ли пользователи для сохранения
            github_parser.save_users_to_db(users)

        total_users_count = github_parser.get_total_users_count()
        print(f"Общее количество пользователей в базе данных: {total_users_count}")
    except Exception as e:
        raise GitHubUserParserException(
            f"Ошибка во время выполнения основной логики: {e}"
        )


def get_command_line_arguments():
    try:
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
    except Exception as e:
        raise ArgumentCommandLineParisngException(
            "Не удалось спарсить аргументы коммандной строки."
        )
