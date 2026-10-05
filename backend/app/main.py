from fastapi import FastAPI

from app.api.routes.recipients import router as recipients_router
from app.api.routes.templates import router as templates_router
from app.api.routes.certificates import router as certificates_router


app = FastAPI(title="Credentia API")

app.include_router(recipients_router)
app.include_router(templates_router)
app.include_router(certificates_router)


@app.get("/")
def root():
    return {"message": "Credentia is alive."}