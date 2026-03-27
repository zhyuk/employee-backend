from pydantic import BaseModel
from datetime import date
from typing import Optional

# === 로그인 스키마 === #
class LoginForm(BaseModel):
    email: str
    password: str

# === 직원 추가 스키마 === #
class addEmployee(BaseModel):
    name: str
    email: str
    password: str
    department: str # 부서
    position: str   # 직급
    hireDate: str   # 입사일자
    phone: Optional[str] = None

# === 이메일 중복검사 스키마 === #
class verifyEmail(BaseModel):
    email: str

# === 개인정보 수정 스키마 === #
class modifyInfo(BaseModel):
    email: str
    department: str # 부서
    position: str   # 직급
    phone: Optional[str] = None
    birthday: date