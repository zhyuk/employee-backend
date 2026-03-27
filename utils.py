import os
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Response, HTTPException
from models import JwtTokens
from sqlalchemy.orm import Session


SECRET_KEY  = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
BCRYPT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def password_encode(password: str):
    """ 비밀번호 인코딩 -> 암호화 작업 """
    return BCRYPT.hash(password)

def password_decode(password: str, hashed_password: str):
    """ 비밀번호 디코딩 -> 암호 해독 작업 """
    return BCRYPT.verify(password, hashed_password)


# ==================== JWT TOKENS ==================== #
ACCESS_TOKEN_EXPIRE = timedelta(minutes=60)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)

def create_access_token(user_id: int, role: str):
    """ JWT 액세스 토큰 생성 """
    exp = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE

    payload = {
        "user_id": user_id,
        "role": role,
        "type": "access",
        "exp": exp  # 만료시간
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token

def create_refresh_token(user_id: int):
    """ JWT 리프레쉬 토큰 생성 """
    exp = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRE

    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": exp  # 만료시간
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return token, exp

def verify_token(token: str, token_type: str):
    """ JWT 토큰 검증 """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user_role = payload.get("role")
        input_token_type = payload.get("type")

        if input_token_type != token_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        return user_id, user_role, None
    
    # 토큰 만료
    except ExpiredSignatureError:
        return None, None, "expired"

    # 유효하지 않는 토큰
    except JWTError:
        return None, None, "invalid"
    
def add_token_for_cookie(user_id: int, role: str, db: Session, response: Response):
    """ JWT 액세스 / 리프레시 토큰 생성 후 쿠키에 추가하는 함수 """
    access_token = create_access_token(user_id, role)
    refresh_token, expire = create_refresh_token(user_id)

    now = datetime.now()

    # 기존 리프레시 토큰 검증
    old_refresh_token = db.query(JwtTokens).filter(JwtTokens.employee_id == user_id, JwtTokens.expires_at > now, JwtTokens.is_revoked == False).first()
    
    # 기존 리프레시 토큰 존재 시 사용불가처리
    if old_refresh_token:
        old_refresh_token.is_revoked = True
        db.commit()

    token = JwtTokens(
        employee_id = user_id,
        refresh_token = refresh_token,
        expires_at = expire
    )

    db.add(token)
    db.commit()

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True
    )
# ==================== JWT TOKENS ==================== #