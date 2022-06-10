import os
from datetime import datetime, timedelta

import jwt
from dotenv.main import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

load_dotenv(verbose=True)


class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = os.getenv('secret')

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=120),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

# class AuthHandler():
#     security = HTTPBearer()
#     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#     secret = os.getenv('secret')
#
#
#     def get_password_hash(self, password):
#         return self.pwd_context.hash(password)
#
#     def verify_password(self, plain_password, hashed_password):
#         return self.pwd_context.verify(plain_password, hashed_password)
#
#     def encode_token(self, user_id):
#         payload = {
#             'exp': datetime.utcnow() + timedelta(days=0, minutes=120),
#             'iat': datetime.utcnow(),
#             'sub': user_id
#         }
#         return jwt.encode(
#             payload,
#             self.secret,
#             algorithm='HS256'
#         )
#
#     def decode_token(self, token):
#         try:
#             payload = jwt.decode(token, self.secret, algorithms=['HS256'])
#             return payload['sub']
#         except jwt.ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail='Signature has expired')
#         except jwt.InvalidTokenError as e:
#             raise HTTPException(status_code=401, detail='Invalid token')
#
#     def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
#         return self.decode_token(auth.credentials)