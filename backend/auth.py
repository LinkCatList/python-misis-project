from datetime import *
from jose import jwt
import os
from fastapi import Depends, HTTPException, Request, status


def get_auth_data():
    return {"secret_key": os.getenv("SECRET_KEY"), "algorithm": os.getenv("ALGORITHM")}

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt

def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token

def get_current_user(token: str = Depends(get_token)):
    try:
        auth_data  = get_auth_data()

    except:
        return