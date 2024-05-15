from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import asyncio
import httpx

app = FastAPI()

class Communicate_Rasa(BaseModel):
    sender:str
    message:str

origins = [
    "http://0.0.0.0",
    "http://0.0.0.0:5500",
    "http://localhost:5500",
    "http://localhost",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/communicate-rasa")
async def talk_to_rasa(data:Communicate_Rasa):
    headers = {"Content-Type": "application/json"}
    print(data.model_dump_json())
    async with httpx.AsyncClient() as client:
        response = await client.post('http://localhost:5005/webhooks/rest/webhook',data=data.model_dump_json(),headers=headers)    
        return JSONResponse(content=response.json(),status_code=status.HTTP_200_OK)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0" , port=5500, log_level="info",reload = True,workers=4)