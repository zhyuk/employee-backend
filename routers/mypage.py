from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from database import get_db
from models import Employee
from schemas.schemas import modifyInfo
from utils import verify_token

router = APIRouter(prefix="/api/mypage")


@router.post("")
def modify_myInfo(res: modifyInfo, db: Session = Depends(get_db), access_token: str = Cookie(None)):
    """
    ----------------------------------------
    [직원용] 개인 인적사항 수정 API
    ----------------------------------------
    """
    user_id, _, _ = verify_token(access_token, "access")

    # if not user_id:
    #     raise HTTPException 

    phoneRegex = res.phone.replace("-", "")

    userInfo = db.query(Employee).filter(Employee.id == user_id).first()

    userInfo.department = res.department
    userInfo.position = res.position
    userInfo.email = res.email
    userInfo.phone = phoneRegex
    userInfo.birthday = res.birthday

    db.commit()    

@router.get("/{id}")
def get_myInfo(id: int, db: Session = Depends(get_db)):
    """
    ----------------------------------------
    [직원용] 개인 인적사항 조회 API
    ----------------------------------------
    """
    # print(id)
    user = db.query(Employee).filter(Employee.id == id).first()

    user_info = {
        "name": user.name,
        "department": user.department,
        "position": user.position,
        "email": user.email,
        "phone": user.phone,
        "birthday": user.birthday,
        "hireDate": user.hireDate,
    }

    return user_info