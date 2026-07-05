from unit_of_work import get_unit_of_work
from controllers.models.user_auth_models import CreateNewAccount, Login


class AuthService:
    @staticmethod
    def register(create_new_account: CreateNewAccount):
        """ユーザを登録"""
        try:
            with get_unit_of_work() as uow:
                # ユーザーIDの重複チェック
                if uow.user_repository.find_by_id(create_new_account.user_id):
                    return {
                        "status": "failed",
                        "message": "このユーザーIDは既に使用されています"
                    }

                user = uow.user_repository.create_user(
                    create_new_account.user_id,
                    create_new_account.password,
                    create_new_account.nickname
                )

                return {
                    "status": "success",
                    "data": {
                        "userId": user.user_id,
                        "userName": user.display_name
                    }
                }
        except Exception as e:
            return {
                "status": "failed",
                "message": "ユーザ登録に失敗しました"
            }

    @staticmethod
    def login(login: Login):
        """ログイン処理"""
        try:
            with get_unit_of_work() as uow:
                user = uow.user_repository.find_by_id(login.user_id)

                if not user:
                    return {
                        "status": "failed",
                        "message": "ユーザが見つかりません"
                    }

                if user.password_hash != login.password:
                    return {
                        "status": "failed",
                        "message": "パスワードが間違っています"
                    }

                return {
                    "status": "success",
                    "data": {
                        "user": {
                            "userId": user.user_id,
                            "userName": user.display_name
                        }
                    }
                }
        except Exception:
            return {
                "status": "failed",
                "message": "ログインに失敗しました"
            }

    @staticmethod
    def get_past_recipients(user_id: str):
        """過去に送信したユーザを取得"""
        try:
            with get_unit_of_work() as uow:
                users = uow.user_repository.find_past_recipients(user_id)

                return {
                    "status": "success",
                    "data": {
                        "users": [
                            {
                                "userId": user.user_id,
                                "userName": user.display_name
                            }
                            for user in users
                        ],
                        "totalCount": len(users)
                    }
                }
        except Exception:
            return {
                "status": "failed",
                "message": "ユーザ取得に失敗しました"
            }