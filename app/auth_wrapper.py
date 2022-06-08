from typing import Optional, Dict
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.exceptions import HTTPException


class AuthWrapperClass(OAuth2PasswordBearer):
    def __init__(self):
        super().__init__(tokenUrl="token")

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param
