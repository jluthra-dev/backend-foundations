from fastapi import FastAPI, HTTPException, status
from typing import Dict, List
from scripts.schemas import User, UserCreate, UserUpdate

app = FastAPI(title="User API Day 3 (in-memory)")

_users: Dict[int, User] = {}
_next_id = 1

def _pydantic_dump(model):
    if hasattr(model, "model dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    if isinstance(model, dict):
        return model
    raise TypeError("Expected a python model or dict, got: " + type(model).__name__)

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    global _next_id

    #email unique check
    for u in _users.values():
        if u.email == payload.email:
            raise HTTPException(status_code=400, detail="Email exists")
        
    user = User(id=_next_id, **_pydantic_dump(payload))
    _users[user.id] = user
    _next_id += 1
    return user

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    user = _users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=List[User])
def list_users():
    return [u for _, u in sorted(_users.items(), key=lambda kv: kv[0])]

@app.put("users/{user_id}", response_model=User)
def replace_user(user_id: int, payload: UserCreate):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    
    for uid, u in _users.items():
        if uid != user_id and u.email == payload.email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
    user = User(id=user_id, **_pydantic_dump(payload))
    _users[user_id] = user
    return user

@app.patch("/users/{user_id}", response_model=User)
def update_user(user_id: int, payload: UserCreate):
    user = _users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    data = _pydantic_dump(user)
    updates = {k: v for k, v in _pydantic_dump(payload).items() if v is not None}

    if 'email' in updates:
        for uid, u in _users.items():
            if uid != user_id and u.email == updates['email']:
                raise HTTPException(status_code=400, detail="Email already exists")
            
    data.update(updates)
    updated = User(**data)
    _users[user_id] = updated
    return updated

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    del _users[user_id]
    return