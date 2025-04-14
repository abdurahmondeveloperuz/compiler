import aiohttp
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
import json

app = FastAPI()

# Enable CORS for all origins (allow requests from anywhere)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Payload structure for executing code in various languages
class CodeRequest(BaseModel):
    language: str
    code: str

# Map language to Glot.io URL and the corresponding file extension
language_urls = {
    "python": ("https://glot.io/run/python?version=latest", ".py"),
    "php": ("https://glot.io/run/php?version=latest", ".php"),
    "javascript": ("https://glot.io/run/javascript?version=latest", ".js"),
    "java": ("https://glot.io/run/java?version=latest", ".java"),
    "c++": ("https://glot.io/run/cpp?version=latest", ".cpp"),
    "c": ("https://glot.io/run/c?version=latest", ".c"),
    "c#": ("https://glot.io/run/csharp?version=latest", ".cs"),
    "bash": ("https://glot.io/run/bash?version=latest", ".sh"),
}

# Function to execute code using Glot.io API
async def run_code(language: str, code: str):
    url, extension = language_urls.get(language, (None, None))
    if not url:
        raise HTTPException(status_code=400, detail="Unsupported language")

    payload = {
        "files": [{"name": f"main{extension}", "content": code}],
        "stdin": "",
        "command": ""
    }
    
    headers = {
        'Content-Type': 'application/json',
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            response_data = await response.json()
            return response_data

# Route to run code based on the selected language
@app.post("/run")
async def execute_code(request: CodeRequest):
    language = request.language.lower()
    code = request.code
    
    try:
        result = await run_code(language, code)
        return result
    except HTTPException as e:
        raise e

# To run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1300)
