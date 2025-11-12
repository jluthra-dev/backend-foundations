from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message" "Hello, FastAPI!"}

@app.get("/users/{user_id}")
def read_user(user_id):
    return {"user_id": user_id, "name": "John Doe"}