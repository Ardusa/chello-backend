from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from models import Account
from utils import hash_password
from schemas import account_model
import uuid
from .db_service import get_db
from .company_service import load_company, create_company_with_details
from schemas.company_model import CompanyBase

from utils import verify_password


def create_account(
    account_data: account_model.AccountCreate,
    db: Session = Depends(get_db)
) -> Account:
    """
    Create a new account in the database.
    This is for creating any account, whether it is a company account or not.
    """
    
    new_account = Account(
        name=account_data.name,
        email=account_data.email,
        password_hash=hash_password(account_data.password),
        position=account_data.position,
        free_plan=account_data.free_plan,
        task_limit=account_data.task_limit,
    )
    
    if account_data.manager_id:
        manager_id = uuid.UUID(account_data.manager_id)
        load_account(account_id=manager_id, db=db)
        new_account.manager_id = manager_id

    if account_data.company_id:
        company_id = uuid.UUID(account_data.company_id)
        load_company(company_id=company_id, db=db)
        new_account.company_id = company_id
        
    if not account_data.create_company:
        new_account.company_id = None
        
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    if not account_data.company_id and account_data.create_company:
        company_data = CompanyBase(
            id=new_account.company_id,
            name=new_account.name,
            founding_member=new_account.id,
            founding_date=new_account.account_created,
        )
        create_company_with_details(company_data=company_data, db=db)
    
    return new_account


def load_account(
    account_id: Optional[uuid.UUID] = None,
    account_id_str: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Account:
    """
    This function is used to load an account from the database. It will throw an error if the query returns no results.
    """
    if account_id_str:
        account_id = uuid.UUID(account_id_str)

    query = db.query(Account)

    if account_id:
        query = query.filter(Account.id == account_id).first()

    elif email:
        query = query.filter(Account.email == email).first()
    
    if not query or (not account_id and not email):
        raise ValueError(
            "Account not found: ", account_id if account_id else email
        )
        

    return query


def create_password(form_data: dict, db: Session = Depends(get_db)):
    """
    This function is used to create a password for a pre-existing account. It will throw an error if the account does not exist.
    """
    user: Account = load_account(account_id=form_data["id"], db=db)

    verify_password(form_data["temporary_password"], user.password_hash)

    user.password_hash = hash_password(form_data["new_password"])
    db.commit()
    db.refresh(user)
    
    return user


def authenticate_account(email: str, password: str, db):
    """
    This function is used to authenticate an account. It will throw an error if anything is incorrect.
    """
    account = load_account(email=email, db=db)

    verify_password(
        plain_password=password, hashed_password=account.password_hash
    )

    return account


def load_accounts(manager: Account, db: Session):
    """
    This function is used to load all accounts for a given manager.
    """
    query = db.query(Account).filter(Account.manager_id == manager.id).all()
    
    return query
