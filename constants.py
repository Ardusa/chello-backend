"""
All Constant Values are defined here
"""

class THRESHOLDS:
    STRONG_THRESHOLD: float= 0.65
    WEAK_THRESHOLD: float= 0.6

class DAG:
    DAG_PATH: str = "Assets/Graphs"
    DAG_EXTENSION: str = ".png"
    DAG_NODE_MULTIPLIER: str = 2.0

class AUTH:
    SECRET_KEY = "CHELLO"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 20
    REFRESH_TOKEN_EXPIRE_MINUTES = 60

class FILE:
    pass

class HOST:
    LOCAL_HOST = "127.0.0.1"
    LAN_HOST = "192.168.0.80"
    
class EMAIL:
    EMAIL_ADDRESS = "example123@chello.team"
    SIGNATURE = "\n\nThanks for your support!\nChello Team"

class DATABASE:
    URL = "sqlite:///./chello.db"