import os
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from dotenv import load_dotenv
from utils import password_encode, password_decode, add_token_for_cookie, verify_token
from models import Employee, JwtTokens
from schemas.schemas import LoginForm

router = APIRouter(prefix="/api")

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")

@router.post("/login")
def check_login(req: LoginForm, res: Response, db: Session = Depends(get_db)):
    """
    ----------------------------------------
    로그인 API
    ----------------------------------------
    """
    # print(req)

    user = db.query(Employee).filter(Employee.email == req.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="아직 가입된 계정이 없어요. 회원가입을 진행해 주세요.")
    if user.is_retired:
        raise HTTPException(status_code=403, detail="퇴사처리된 계정은 사용할 수 없습니다. 관리자에게 문의하세요.")
    else:
        if not password_decode(req.password, user.password):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않아요.")
        
    add_token_for_cookie(user.id, user.role, db, res)
        
    return {"role": user.role}
        
@router.get("/me")
def verify_tokens(access_token: str = Cookie(None)):
    """
    ----------------------------------------
    JWT 토큰 검증 API
    ----------------------------------------
    """

    if not access_token:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    user_id, user_role, msg = verify_token(access_token, "access")

    return {"role": user_role, "id": user_id}

@router.post("/logout")
def logout(res: Response, access_token: str = Cookie(None), refresh_token: str = Cookie(None), db: Session = Depends(get_db)):
    """
    ----------------------------------------
    로그아웃 API
    ----------------------------------------
    """

    if refresh_token:
        token = db.query(JwtTokens).filter(JwtTokens.refresh_token == refresh_token, JwtTokens.is_revoked == False).first()

        if token:
            token.is_revoked = True
            db.commit()

    res.delete_cookie(key="refresh_token",secure=True, samesite="none", path="/")
    res.delete_cookie(key="access_token", secure=True, samesite="none", path="/")

    res.status_code = 200
