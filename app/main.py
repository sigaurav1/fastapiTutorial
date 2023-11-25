from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
from sqlalchemy.orm import Session
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

my_posts = [
    {
        "title" : 'post 1',
        'id': 1
    },
    {
        "title" : 'post 2',
        'id': 2
    }
]
def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

def find_index_post(id):

    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
class Post(BaseModel):
    title: str
    content: str
    published: Optional[bool]

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

@app.get('/sqlalchemy')
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {'data':posts}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data":posts}

@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_posts(posts: Post):
    cursor.execute("""INSERT INTO posts (title, content, published)
                    VALUES(%s, %s, %s) RETURNING *""", (posts.title, posts.content, posts.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data" : new_post}

@app.get('/posts/{id}')
def get_post(id: int, response: Response):
    cursor.execute(f"""SELECT * from posts where id = {id}""")
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} was not found')
    return {'post_detail': post}

@app.delete("/posts/{id}")
def delete_post(id: int, status_code = status.HTTP_204_NO_CONTENT):
    cursor.execute(f"""DELETE from posts where id = {id} returning *""")
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'Post with id {id} does not exist')
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} does not exist')
    return post

