from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> str:
    """
    This function is used to verify a password against a hashed password. It will raise a ValueError if the password is incorrect
    """
    password_is_good = pwd_context.verify(plain_password, hashed_password)
    if not password_is_good:
        raise ValueError("Password is incorrect")
    
    return plain_password
