from sqlalchemy import  Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, func, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from database import SessionLocal

class Employee(Base):
    __tablename__ = "employees"

    

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False)    # 이메일
    password = Column(String(255), nullable=False)  # 비밀번호
    name = Column(String(50), nullable=False)   # 이름
    phone = Column(String(20), nullable=True)   # 전화번호
    department = Column(String(20), nullable=True) # 부서
    position = Column(String(20), nullable=True)   # 직급
    hireDate = Column(Date, server_default=func.now())  # 입사일
    role = Column(String(10), server_default="employee")    # 역할
    is_retired = Column(Boolean, default=False)  # 재직여부
    birthday = Column(Date, nullable=True)

    tokens = relationship("JwtTokens", back_populates="employee", cascade="all, delete-orphan")

class JwtTokens(Base):
    __tablename__ = "jwt_tokens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    refresh_token = Column(String(512)) # 리프레시 토큰
    expires_at = Column(DateTime, nullable=True)    # 만료일자
    is_revoked = Column(Boolean, server_default="false")    # 사용가능여부
    created_at = Column(DateTime, server_default=func.now())    # 생성일자

    employee = relationship("Employee", back_populates="tokens")