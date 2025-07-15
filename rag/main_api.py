from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from rag.api.chat_router import chat_router


app = FastAPI()

app.include_router(chat_router, prefix="/v1")

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")