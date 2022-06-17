from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import xmltodict

app = FastAPI()


@app.post("/files/")
def create_files(files: bytes = File()):

    data =  xmltodict.parse(files)
    return data


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
