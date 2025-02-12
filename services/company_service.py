from typing import Optional
from models import Company
import uuid
from sqlalchemy.orm import Session
from fastapi import Depends
from .db_service import get_db


def load_company(
    company_id: Optional[uuid.UUID] = None,
    company_id_str: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Optional[Company]:
    """
    This function is used to load a company from the database. It will throw an error if the query returns no results.
    """
    if company_id_str:
        company_id = uuid.UUID(company_id_str)

    query = db.query(Company)

    if company_id:
        query = query.filter(Company.id == company_id).first()
        
    if not query:
        raise ValueError("Company not found: ", company_id)
    
    return query