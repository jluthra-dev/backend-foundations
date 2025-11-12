from fastapi import FastAPI, HTTPException
from schemas import User, UserCreate

app = FastAPI()
users = []

@app.post("/users", response_model=User)
def create_user(user: UserCreate):
    new_user = User(id=len(users)+1, **user.dict())
    users.append(new_user)
    return new_user

@app.get("/users", response_model=list[User])
def list_users():
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")