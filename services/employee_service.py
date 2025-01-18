from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from models import Employee, Company
from utils import hash_password
from services import get_db
from schemas import api_schemas
import uuid

from utils import verify_password

def create_employee(employee: Employee, db: Session = Depends(get_db)) -> Employee:
    if employee.manager_id and not db.query(Employee).filter(Employee.id == employee.manager_id).first():
        raise HTTPException(status_code=400, detail="Manager ID does not exist")
    
    if employee.company_id and not db.query(Company).filter(Company.id == employee.company_id).first():
        raise HTTPException(status_code=400, detail="Company ID does not exist")
    
    employee.password_hash = hash_password(employee.password_hash)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

def register_account(employee_data: api_schemas.CreateNewAccountForm, db: Session = Depends(get_db)):
    company_id = uuid.uuid4()
    
    company = Company(id=company_id, name=employee_data.company_name, founding_member=None)
    employee = Employee(
        name=employee_data.name,
        email=employee_data.email,
        password_hash=hash_password(employee_data.password),
        company_id=company_id,
        position=employee_data.position,
        manager_id=None,
    )

    db.add(employee)
    db.commit()
    
    company.founding_member = employee.id
    db.add(company)
    db.commit()
    
    db.refresh(company)
    db.refresh(employee)

    return employee

def load_employee(
    employee_id: Optional[int] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Optional[Employee]:
    
    if employee_id:
        return db.query(Employee).filter(Employee.id == employee_id).first()
    if email:
        return db.query(Employee).filter(Employee.email == email).first()
    return None

def create_password(form_data: dict):
    user: Employee = load_employee(employee_id=form_data["id"])

    if not user:
        raise ValueError("Invalid Link, Employee ID not found")

    if not verify_password(form_data["temporary_password"], user.password_hash):
        raise ValueError("Invalid Temporary Password")

    user.password_hash = hash_password(form_data["new_password"])

def authenticate_employee(email: str, password: str, db):
    employee = load_employee(email=email, db=db)
    if not employee:
        print("Employee account not found: ", email)
        return False

    passGood = verify_password(
        plain_password=password, hashed_password=employee.password_hash
    )
    # passGood = employee.verify_password(password=password)
    if not passGood:
        print("Password incorrect: ", password)
        return False

    return employee