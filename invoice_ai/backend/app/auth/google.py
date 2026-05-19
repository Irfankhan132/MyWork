from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_CLIENT_ID = "YOUR_CLIENT_ID"

def verify_google_token(token: str):
    idinfo = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        GOOGLE_CLIENT_ID
    )

    return {
        "google_id": idinfo["sub"],
        "email": idinfo["email"],
        "name": idinfo.get("name"),
        "picture": idinfo.get("picture"),
    }


@router.post("/auth/google")
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    user_info = verify_google_token(payload.id_token)

    user = get_or_create_user(
        db,
        google_id=user_info["google_id"],
        email=user_info["email"],
        name=user_info["name"],
    )

    token = create_jwt(user)

    return {
        "access_token": token,
        "user": user
    }
