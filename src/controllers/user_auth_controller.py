from fastapi import FastAPI
from services.auth_service import AuthService
from controllers.models.user_auth_models import CreateNewAccount, Login

app = FastAPI()


@app.post("/create/new_account")
def create_account(create_new_account: CreateNewAccount):
    return AuthService.register(create_new_account)


@app.post("/login")
def login(login_value: Login):
    return AuthService.login(login_value)