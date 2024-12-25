import argparse

from githubparser import GitHubUserParser
from exceptions import GitHubUserParserException, ArgumentCommandLineParsingException


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
        raise ArgumentCommandLineParsingException(
            "Не удалось спарсить аргументы коммандной строки."
        )
