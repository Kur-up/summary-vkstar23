from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .api import users_router
from .api import planets_router

title = "summary-vkstar23"
description = """# VK mini app - Star23 #
The project was created while working in the Trend Surfers Agency web-studio.<br>
Backend mini-application of the social network VKontakte,<br>
for playing on the holiday Cosmonautics Day.
<br><br>
Technologies and stack: 
* FastAPI
* PostgresSQL
* Alembic
* SQLAlchemy
* Docker

The version is different from the original.<br>
Some changes have been made to the logic,<br> 
code has been refactored and unused endpoints and dependencies have been removed."""

app = FastAPI(
    title=title,
    description=description,
    version="1.0.0",
    contact={
        "name": "Lev Kurapov",
        "url": "https://github.com/kur-up",
        "email": "kurup.performance@gmail.com",
    },
)

app.include_router(users_router, prefix="/users")
app.include_router(planets_router, prefix="/planets")


@app.get("/health", include_in_schema=False)
async def health_get():
    return JSONResponse(status_code=200, content="OK")
