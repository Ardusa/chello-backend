from typing import Optional
from models import Company
import uuid
from sqlalchemy.orm import Session
from fastapi import Depends
from .db_service import get_db
from schemas.company_model import CompanyCreate, CompanyBase


def load_company(
    company_id: Optional[uuid.UUID] = None,
    company_id_str: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Company:
    """
    This function is used to load a company from the database. It will throw an error if the query returns no results.
    """
    if company_id_str:
        company_id = uuid.UUID(company_id_str)

    query = db.query(Company)

    if company_id:
        query = query.filter(Company.id == company_id).first()
        
    if not query or not company_id:
        raise ValueError("Company not found: ", company_id)

    return query

def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
) -> Company:
    """
    Create a new company in the database. 
    """
    new_company = Company(
        name=company_data.name,
        founding_member=uuid.UUID(company_data.founding_member),
        task_limit=company_data.task_limit,
        logo=company_data.logo,
    )
    
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    
    return new_company

def create_company_with_details(
    company_data: CompanyBase,
    db: Session = Depends(get_db),
) -> Company:
    """
    Create a new company in the database. 
    """
    new_company = Company(
        id=company_data.id,
        name=company_data.name,
        founding_member=company_data.founding_member,
        founding_date=company_data.founding_date,
    )
    
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    
    return new_company

def fetch_logo(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Optional[str]:
    """
    Fetch the logo of a company from the database.
    """
    company = load_company(company_id=company_id, db=db)
    return company.logo