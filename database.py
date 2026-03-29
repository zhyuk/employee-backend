import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?sslmode=require&channel_binding=require"
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,  # 연결 유효성을 체크 후 쿼리 실행
    pool_recycle=3600,   # 1시간마다 연결 재사용 (연결 만료 방지)
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False,)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    import models
    Base.metadata.create_all(bind=engine)
    print("DB 연결 성공")

def create_admin():
    """
    기본으로 사용할 관리자 계정을 생성하는 함수입니다.
    """
    from models import Employee
    from utils import password_encode

    db = SessionLocal()

    try:
        admin_exists = db.query(Employee).filter(Employee.email == "admin@bit.com", Employee.name == "관리자").first()
        
        if not admin_exists:
            admin = Employee(
                email = "admin@bit.com",
                password = password_encode("1111"),
                name = "관리자",
                role = "admin"
            )

            employee = [Employee(
                email = "emp1@bit.com",
                password = password_encode("1111"),
                name = "김사원",
                phone = "01012345678",
                department = "개발팀",
                position = "사원",
                birthday = datetime(1995, 5, 20),
                is_retired = True
            ), Employee(
                email = "emp2@bit.com",
                password = password_encode("1111"),
                name = "최팀장",
                phone = "01023456789",
                department = "지원팀",
                birthday = datetime(1998, 1, 2),
                position = "팀장"
            )
            ]

            db.add(admin)
            db.add_all(employee)
            db.commit()
            print("관리자 계정 생성 완료")
        else:
            print("관리자 계정이 이미 존재합니다.")

    except Exception as e:
        print(f"에러 발생: {e}")
        db.rollback()
    finally:
        db.close()
