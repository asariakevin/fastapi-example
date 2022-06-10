from typing import Callable, Union , List

from fastapi import FastAPI
from pydantic import BaseModel

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import insert, select , update  , delete

app = FastAPI()

engine = create_engine("mysql+pymysql://root:jenga@localhost/test")
metadata = MetaData()

user_table = Table(
        "user_account",
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name',String(30)),
        Column('fullname',String(50)),
        )

metadata.create_all(engine)

class UserRequestBody(BaseModel):
    name: str
    fullname: str
    

@app.get("/")
def read_root():
    return {"Hello": "world"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str,None] = None):
    return {"item_id": item_id, "q": q}

# user crud app
@app.get("/users/{user_id}")
def read_user(user_id: int, q: Union[str,None] = None):
    query = select(user_table).where(user_table.c.id == user_id)

    name = "Nameless"
    with engine.begin() as connection:
        result = connection.execute(query)
        for row in result:
            name = row.fullname
    return {"user_id": user_id, "fullname": name}

@app.post("/users/")
def create_user(user: UserRequestBody):
    if add_user_to_db(user):
        return {"status": "inserted"}
    else:
        return {"status": "error occured"}
        
@app.get("/users/")
def get_all_users():
    users = []
    with engine.begin() as connection:
        result = connection.execute(select(user_table))
        users =result.all()
    return users

@app.put("/users/{user_id}")
def update_user(user_id: int, user_info: UserRequestBody):
    with engine.begin() as connection:
          connection.execute(update(user_table).where(user_table.c.id == user_id), user_info.dict())
    return {"action": "done"}
    
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    delete_statement = delete(user_table).where(user_table.c.id == user_id)
    done = db_connection_wrapper([delete_statement])
    if done:
        return {"response" : f"deleted ID:{user_id}"}
    else:
        return {"response" : f"Unable to deleted ID: {user_id}"}
    
    
def add_user_to_db(user: UserRequestBody) -> bool:
    done = False
    with engine.begin() as connection:
        connection.execute(insert(user_table), user.dict())
        done = True
    return done

def add_user_to_db_callable(user: UserRequestBody) -> bool:
    db_connection_wrapper([insert(user_table), user.dict()])

def db_connection_wrapper(execute_params: List) -> bool:
    done = False
    with engine.begin() as connection:
        connection.execute(*execute_params)
        done = True
    return done