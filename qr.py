import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pyqrcode import QRCode
import io
from starlette.responses import StreamingResponse
from urllib.parse import quote as urllibquote

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/qr/{query}", response_class=HTMLResponse)
async def genpage(request: Request, query: str):
    # строка query имеет строгий формат: FdIdOdDDMMYYYYddmmyyyy
    # F,I,O - первая буква фамилии, имени, отчества
    # d - количество звездочек (длина фамилии-1) например Харитонова Ульяна Йорковна => Х9У5Й7 отобразится как 
    # Х********* У***** Й******* 
    # DDMMYYYY - дата рождения
    # ddmmyyyy - срок действия
    fio = query[0] + '*' * int(query[1]) + ' '\
        + query[2] + '*' * int(query[3]) + ' '\
        + query[4] + '*' * int(query[5])
    
    birthday = query[6:8] + '.' + query[8:10] + '.' + query[10:14]
    expired = query[14:16] + '.' + query[16:18] + '.' + query[18:22]
    
    return templates.TemplateResponse("qr.j2.html", {"request": request, "fio": fio, "birthday": birthday, "expired": expired})

@app.get("/create/{query}", response_class=HTMLResponse)
async def genqrcode(request: Request, query: str):
    url = request.url
    path = "/qr/" + urllibquote(query)
    urlstr = f'{url.scheme}://{url.netloc}{path}'
    
    qr = QRCode(urlstr)

    buffer = io.BytesIO()
    qr.png(buffer, scale=8)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)