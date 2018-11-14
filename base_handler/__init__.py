
from config import CFG as O_O
if O_O.auth_storage =='JWT':
    from base_handler.jwt_handler import BaseJWTHandler as BaseAuthHandler, jwt_auth as auth
else:
    from base_handler.session_handler import BaseSessionHandler as BaseAuthHandler, session_auth  as auth
