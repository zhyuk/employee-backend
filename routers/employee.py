import os
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from database import get_db
from models import Employee
from schemas.schemas import addEmployee, verifyEmail
from utils import password_encode
from datetime import date

router = APIRouter(prefix="/api/employees")

@router.get("")
def get_employeeList(db: Session = Depends(get_db)):
    """
    ----------------------------------------
    직원 목록 조회 API
    ----------------------------------------
    """

    # 관리자 정보는 리턴 X
    employees = db.query(Employee).filter(Employee.role == "employee").order_by(Employee.id.desc()).all()

    result = [
    {
        "id": emp.id,
        "name": emp.name,
        "email": emp.email,
        "department": emp.department,
        "position": emp.position,
        "hireDate": emp.hireDate.strftime('%Y-%m-%d') if emp.hireDate else None,
        "phone": emp.phone,
        "is_retired": emp.is_retired,
        "birthday": emp.birthday
    }
    for emp in employees
    ]

    return result

@router.post("")
def add_employee(data: addEmployee, db: Session = Depends(get_db)):
    """
    ----------------------------------------
    직원 추가 API
    ----------------------------------------    
    """
    # print(data)

    employee = Employee(
        email = data.email,
        password = password_encode(data.password),
        name = data.name,
        department = data.department,
        position = data.position,
        hireDate = data.hireDate if data.hireDate else date.today(),
        phone = data.phone.replace("-", "") if data.phone else None,
        birtday = data.birthday
    )

    db.add(employee)
    db.commit()

@router.post("/verify-email")
def verify_email(data: verifyEmail, db: Session = Depends(get_db)):
    """
    ----------------------------------------
    이메일 중복검사 API
    ----------------------------------------    
    """
    employee = db.query(Employee).filter(Employee.email == data.email).first()

    if employee:
        raise HTTPException(status_code=409, detail="이미 존재하는 이메일입니다.")

@router.get("/status/{employee_id}")
def modify_status(employee_id: int, db: Session = Depends(get_db)):
    """
    ----------------------------------------
    직원 퇴사처리 API
    ----------------------------------------
    """

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    employee.is_retired = True

    db.commit()


@router.get("{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    ----------------------------------------
    직원 상세조회 API
    ----------------------------------------
    """

    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    employee_info = {
        "name": employee.name,
        "email": employee.email,
        "department": employee.department,
        "position": employee.position,
        "birthday": employee.birthday,
        "hireDate": employee.hireDate,
        "is_retired": employee.is_retired
    }

    return employee_info