import json
import uuid
from os import listdir
from pathlib import Path
from mimetypes import guess_type, guess_extension
from io import BytesIO

from aiohttp import web

route = web.RouteTableDef()

FILES_DIR = Path(__file__).parent / "files"

if not FILES_DIR.exists():
    FILES_DIR.mkdir()

data = {}


def read_data():
    with open("data.json", "r", encoding="utf8") as f:
        data.update(json.load(f))


def write_data():
    with open("data.json", "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


try:
    read_data()
except (json.JSONDecodeError, FileNotFoundError):
    write_data()


@route.get("/file/{filename}")
async def return_file(request: web.Request):
    filename = request.match_info["filename"]

    if filename not in listdir(FILES_DIR):
        return web.json_response(
            {
                "errorDescription": "Cannot found this file"
            },
            status=404
        )
    with open(FILES_DIR / filename, "rb") as f:
        return web.Response(
            body=f.read(),
            content_type=data[filename]
        )


@route.post("/file")
async def load_file(request: web.Request):
    post = await request.post()

    files = {}

    for key, value in post.items():
        if isinstance(value, web.FileField):
            file_id = str(uuid.uuid4()) + "." + value.filename.rsplit(".", maxsplit=1)[-1]
            with open(FILES_DIR / file_id, "wb") as file:
                file.write(value.file.read())
            files[key] = file_id
            data[file_id] = guess_type(value.filename)[0]

    write_data()

    if not files:
        return web.json_response(
            {"errorDescription": "No file found"},
            status=400
        )

    return web.json_response(
        {"files": files}
    )


app = web.Application()

app.add_routes(route)

if __name__ == "__main__":
    web.run_app(app, port=80)
