from fastapi import FastAPI
from . import models, auth
from .database import engine
from psycopg2.extras import RealDictCursor
import psycopg2
from .routers import post, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

try:
    pg_connection_dict = {
        'dbname': 'fastapi',
        'user': 'postgres',
        'password': 'root',
        'host': 'localhost',
        'cursor_factory': RealDictCursor
    }
    conn = psycopg2.connect(**pg_connection_dict)
    cursor = conn.cursor()
    print('DB Connection successful')
except Exception as error:
    print('Connecting to the database failed')
    print('Error ', error)


@app.get('/')
async def root():
    return {"message":"Welcome to my start"}