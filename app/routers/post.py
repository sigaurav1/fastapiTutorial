from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schema, oauth2
from sqlalchemy.orm import Session
from .. database import  get_db

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

@router.get('/', response_model=List[schema.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    posts = db.query(models.Post).all()
    # posts = cursor.fetchall()
    return posts

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schema.Post)
def create_posts(posts: schema.PostCreate, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(**posts.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    # cursor.execute("""INSERT INTO posts (title, content, published)
    #                 VALUES(%s, %s, %s) RETURNING *""", (posts.title, posts.content, posts.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    return new_post

@router.get('/{id}')
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(f"""SELECT * from posts where id = {id}""")
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} was not found')
    return post

@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(f"""DELETE from posts where id = {id} returning *""")
    # post = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'Post with id {id} does not exist')
    post.delete(synchronize_session = False)
    db.commit()
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@router.put('/{id}')
def update_post(id: int, post: schema.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} does not exist')

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()