import models
import json
import shutil
import os.path
from typing import List, Optional
from models import Users, Tags
from typing import Optional
from fastapi import FastAPI, Request, Depends, File, UploadFile, Body
from pydantic import BaseModel
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from sqlalchemy import delete
from sqlalchemy import insert 
from sqlalchemy import update
from sqlalchemy.orm.exc import NoResultFound
from auth import generate_uid
from datetime import datetime 
# May need to import this library below, but right now, it isn't being used:
# from sqlalchemy.orm.exc import MultipleResultsFound

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class UserRegister(BaseModel):
    id : int
    username : str
    password : str
    email : str

class UserLogin(BaseModel):
    username : str
    password : str

class TagInfo(BaseModel):
    user : str
    title : str
    region : str
    location : str 
    n_likes : int
    caption: str
    song : str # url ?
    # caption : str

    # Pydantic vs UploadFile fix
    # https://github.com/tiangolo/fastapi/issues/2257
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally: 
        db.close()

# Homepage

@app.get("/")
async def root():
    # insert homepage info here
    return {"message": "Hello World"}

# Sign Up 
@app.post("/registerUser")
async def registerUser(userReg: UserRegister, db: Session = Depends(get_db)):
    register = Users()
    #register.id = generate_uid()
    register.username = userReg.username
    register.password = userReg.password
    register.email = userReg.email

    try:
        # Check if username exists
        db.query(Users).filter(Users.username == userReg.username).one()
        db.commit()
        return {"username already exists": userReg.username}
    except NoResultFound:
        # Check if email exists
        try:
            db.query(Users).filter(Users.email == userReg.email).one()
            db.commit()
            return {"email already exists": userReg.email}
        except NoResultFound:
            # Create user if details don't exist
            db.add(register)
            db.commit()
            return {"user created": userReg.username}

# Log In
@app.post("/login")
async def loginUser(login: UserLogin, db: Session = Depends(get_db)):
    db.query(Users).filter(Users.username == login.username, Users.password == login.password)
    try:
        # Check username to login with username
        db.query(Users).filter(Users.username == login.username).one()
        db.commit()
        try:
            # If username matches, check password
            db.query(Users).filter(Users.username == login.username, Users.password == login.password).one()
            db.commit()
            return {"user login successful": login.username}
        except NoResultFound:
            return {"incorrect password": login.username}
    except NoResultFound:
        return {"user does not exist": login.username}

# Publish New Tag
@app.post("/publishTag")
async def publishTag(tagInf : TagInfo = Body(...), db: Session = Depends(get_db), img: UploadFile = File(None)):
    tg = Tags()
    tg.id = 0
    while (True):
        try:
            # if id already exists then +1 to number
            db.query(Tags).filter(Tags.id == tg.id).one()
            db.commit()
            tg.id+=1
        except NoResultFound:
            break

    tg.user = tagInf.user
    tg.title = tagInf.title
    tg.region = tagInf.region
    tg.location = tagInf.location
    tg.n_likes = tagInf.n_likes
    tg.caption = tagInf.caption
    tg.song = tagInf.song
    tg.time_made = datetime.now()
    tg.time_edited = tg.time_made
    tg.image = -1 # -1 if image isn't uploaded
    
    if img:
        # Save to image to folder in backend
        imageIndex=0
        path = "Images/" + str(imageIndex)
        while (os.path.exists(path)):
            imageIndex+=1
            path = "Images/" + str(imageIndex)

        tg.image = imageIndex
        with open(path, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)

    db.add(tg)
    db.commit()    
    
    return {"tag posted": tg.title}

# Generate Random Tag
#@app.get()
#async def generateRandomTag(db: Session = Depends(get_db)):

# View All My Tags
#@app.get()
#async def viewAllMyTags(db: Session = Depends(get_db)):

# filter for certain posts to appear

# search for tags and music

# Delete User 
@app.delete("/deleteUser")
async def deleteUser(userReg: UserRegister, db: Session = Depends(get_db)):
    # Not for functionality of website, just for deleting Users
    if (db.query(Users).filter(Users.username == userReg.username).delete()):
        db.commit()
        return {"user deleted": userReg.username}
    else: 
        return {"no user found": None}

# Change Username
"""
@app.put("/changeUsername")
async def changeUsername(db: Session = Depends(get_db)):
    # need an input new username

    try:
        # Check if username exists
        db.query(Users).filter(Users.username == userReg.username).one()
        db.commit()
        try:
            # update username

            return {"username uodated": }
    except NoResultFound:
        return {"no user found with username": None}
"""

# Change Password
"""
@app.put("/changePassword")
async def changePassword(db: Session = Depends(get_db)):
    # need an input new password

    try:
        # Check if username exists
        db.query(Users).filter(Users.username == userReg.username).one()
        db.commit() 
        # check if password exists
        if password exists:    
            # update password
            return {"password uodated": }
        else:
            return {"password has already been used": None}
    except NoResultFound:
        return {"no user found with username": None}
"""

# Link to Spotify
"""
@app.get("/linkSpotify")
async def linkSpotify(db: Session = Depends(get_db)):
    # Get Spotify login token

    # Add Spotify token to user
"""

# TO DO:
# - Change username 
# - Change password
# - Logout (not sure what to do or if implementation is needed for this in backend)
# Filter tags by info
"""
A additional attribute will be needed -> logged_in (True/False)
"""
# - Link to Spotify

# - Generate Random Tag
# - View All My Tags
# - Filter for certain posts to appear
# - Search for tags and music
# - Reset forgotten password
# - Liking a post
# - Add message/comment to new tag
# - View notifications

