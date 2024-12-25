from utils import run_github_fetcher, get_command_line_arguments


def main():
    try:
        command_line_arguments = get_command_line_arguments()
        run_github_fetcher(query=command_line_arguments.query)
    except SystemExit as e:
        print("Ошибка при обработке аргументов командной строки.")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    main()
