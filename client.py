from pathlib import Path
from mimetypes import guess_type
from json import loads

from requests import post, get
from requests_toolbelt import MultipartEncoder


DOWNLOAD_DIR = Path(__file__).parent / "downloads"
if not DOWNLOAD_DIR.exists():
    DOWNLOAD_DIR.mkdir()


def upload_file(host: str, file_path: Path) -> str:
    encoder = MultipartEncoder(
        fields={file_path.name: (file_path.name, file_path.open("rb"), guess_type(file_path.name))}
    )

    response = post(host + "file", data=encoder, headers={'Content-Type': encoder.content_type})

    filename = loads(response.text)["files"][file_path.name]

    return filename


def download_file(host: str, filename: str) -> Path:
    response = get(host + "file/" + filename)

    file_path = DOWNLOAD_DIR / filename

    with file_path.open("wb") as file:
        file.write(response.content)

    return file_path


def main():
    host = input("Введіть адресу файлового хостингу з яким ви будете взаємодіяти\n>>> ")

    if not host.startswith("http"):
        host = "http://" + host

    if not host.endswith("/"):
        host += "/"

    while 1:
        action = input(
            "Виберіть те, що ви збираєтесь зробити:\n"
            "[1] Завантажити файл\n"
            "[2] Звантажити файл\n"
            "[3] Вийти\n"
            ">>> "
        )

        if action == "1":
            file_path = Path(input("Введіть повну адресу до файлу\n>>> "))

            if not file_path.exists():
                print("Цього файлу не існує!")
                continue

            name = upload_file(host, file_path)

            print("Ім'я файлу на файловому хостингу:", name)
            print("Посилання на файл:", host + "file/" + name)

        elif action == "2":
            filename = input("Введіть ім'я файлу на файловому хостингу\n>>> ")

            path = download_file(host, filename)

            if path == -1:
                print("Цього файлу не існує")
                continue

            print("Адреса звантаженого файлу:", path.absolute())

        elif action == "3":
            print("Допобачення!")
            exit()

        else:
            print("Нема такої дії")


if __name__ == "__main__":
    main()
