from fastapi import Depends, Header, HTTPException

API_KEY = "adminsecret123"

def verify_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Accès non autorisé")