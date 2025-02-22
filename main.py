from fastapi import FastAPI
import requests
import uvicorn

app = FastAPI()

@app.get("/")
async def hello():
    # Example of using requests library
    response = requests.get('https://api.github.com/zen')
    return {"message": f"Hello from Cloud Run! Here's some wisdom: {response.text}"}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080) 