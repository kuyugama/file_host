import socket
import uuid
from os import listdir
from pathlib import Path

from aiohttp import web

route = web.RouteTableDef()

FILES_DIR = Path(__file__).parent / "files"

if not FILES_DIR.exists():
    FILES_DIR.mkdir()


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

    return web.FileResponse(FILES_DIR / filename)


@route.post("/file")
async def load_file(request: web.Request):
    post = await request.post()

    files = {}

    for key, value in post.items():
        if isinstance(value, web.FileField):
            file_id = str(uuid.uuid4())
            with open(FILES_DIR / file_id, "wb") as file:
                file.write(value.file.read())
            files[key] = file_id

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
    web.run_app(app, port=80, host=socket.gethostbyname(socket.gethostname()))
