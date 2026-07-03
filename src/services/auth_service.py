from sqlalchemy.orm import Session

class AuthService:
  @staticmethod
  def register(user_id, password, name):
    """
    ユーザを登録する
    """
    #TODO:UserRepositoryクラスのcreateUser(user_id, password, name)メソッドを呼び出す
    #TODO:返却された値を変数に代入し、返却値を作成、返却する
    return {
      "status": "success",
      "data": {
        "token": "eyJhbGciOiJIUzI1Ni...", 
        "user": { "userId": "user_001", "userName": "田中 太郎"}
      }
    }
  
  @staticmethod
  def login(user_id, password):
    """
    ログイン処理を行う
    """
  #TODO:UserRepositoryクラスのfindPasswordById(user_id)を呼び出し、値を引数に代入する
  #TODO:代入されたパスワードと引数に指定されたpasswordを照会する
  #TODO:照会が成功した場合は、UserRepositoryクラスのfindUserById(user_name)を呼び出し、返却されたオブジェクトを変数に代入する
  #TODO:トークンを生成する
  #TODO:値を生成し、返却する
    return{
      "status": "success",
      "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "user": {"userId": "user_001", "userName": "田中 太郎"}
      }
    }
  
  @staticmethod
  def getPastRecipients(user_id):
    """
    過去に送信したユーザを取得する
    """
  #TODO:UserRep9ositoryクラスのfindPastRecipients(user_id)を呼び出し、返却された値を変数に代入する
  #TODO:変数をもとに返却値を生成し、返却する
    return {
      "status": "success",
      "data": {
        "users": [
          {"userId": "user_004","userName": "高橋 次郎"},
          {"userId": "user_005","userName": "伊藤 美咲"}
        ],
        "totalCount": 2
      }
    }