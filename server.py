import uvicorn

if __name__ == '__main__':
    uvicorn.run("app:asgi_app", reload=False)
