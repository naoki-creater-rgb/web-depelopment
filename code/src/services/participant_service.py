from pydantic import BaseModel

class ParticipantService:
  @staticmethod
  def getParticipatingEvents(user_id):
    """
    ユーザが参加しているイベントを取得する
    """
    #TODO:EventRepositoryクラスのfindEventsByManagerId(manager_id)メソッドを呼び出す
    #TODO:Eventオブジェクトの属性statusごとに異なる配列にオブジェクトを格納する
    #TODO:返却値を生成して、返却する
    return {
      "status": "success",
      "data": {
        "unanswered": [
          {
            "eventId": 101,
            "eventName": "新年会2026",
            "deadlineForResponses": "2026-03-10 15:00",
            "managerName": "幹事 太郎"
          }
        ],
        "answered": [
          {
            "eventId": 102,
            "eventName": "28卒同窓会",
            "deadlineForResponses": "2026-03-15 17:00",
            "managerName": "幹事 次郎"
          },
          {
            "eventId": 99,
            "eventName": "忘年会2025",
            "datetime": "2025-12-01 19:00",
            "managerName": "幹事 太郎"
          }
        ]
      }
    }
  
  @staticmethod
  def getEventDetails(event_id):
    """
    イベント詳細を取得する（回答用）
    """
    #TODO:EventRepositoryクラスのfindEventDetailById(event_id)メソッドを呼び出し、値を変数に代入する
    #TODO:返却値を生成して、返却する
    return {
      "status": "success",
      "data": {
        "eventId": 101,
        "eventName": "新年会2026",
        "managerName": "hanyunaoki",
        "description": "今年の新年会です。希望の日程とエリアを教えてください！",
        
        "candidateDates": [
          { "dateCandidateId": 1, "datetime": "2026-04-01 19:00" },
          { "dateCandidateId": 2, "datetime": "2026-04-05 18:30" }
        ],
        "candidateAreas": ["新宿", "渋谷", "池袋"]
      }
    }
    
  # 日程ごとの回答を定義する型（型ヒント用）
  class DateResponseInput(BaseModel):
      candidate_id: str
      score: int
      comment: str

  @staticmethod
  def submitResponse(event_id, user_id, budget, area_id, general_comment, date_responses: list[DateResponseInput]):
     """
     アンケート結果をテーブルに追加する
     """
     #TODO:EventParticipantRepositoryクラスのupdateParticipantBaseResponse(event_id, user_id, bodget, area_id, general_comment)を呼び出す
     #TODO:EventParticipantRepositoryクラスのupsertDateResponse(event_id, user_id, date_responses[?].candidate_id, date_responses[?].score, date_responses[?].comment)を呼び出す。date_responsesの数だけ実行
     #TODO:返却値を作成して、値を返す
     return {
      "status": "success",
      "message": "回答を保存しました",
      "data": {
        "eventId": 101,
        "eventName": "新年会2026",
        
        "dateResponses": [
          { "dateCandidateId": 1, "datetime": "2026-04-01 19:00", "score": 5, "comment": "いつでもOK" },
          { "dateCandidateId": 2, "datetime": "2026-04-05 18:30", "score": 0, "comment": "出張のため不可" }
        ],
        "preferredBudget": 5000,
        "preferredArea": {"area_id": 1, "area": "新宿"},
        "overallComment": "楽しみにしてます！"
      }
    }
  
  @staticmethod
  def getConfirmedDetails(event_id):
     """
     確定済みのイベント情報を取得する
     """
    #TODO:EventRepositoryクラスのfindEventDetailById(event_id)を呼び出し、値を変数に代入する
    #TODO:返却値を作成して、値を返す
     return {
      "status": "success",
      "data": {
        "eventId": 101,
        "eventName": "新年会2026",
        "managerName": "hanyunaoki",
        
        "confirmedDetails": {
          "datetime": "2026-04-01 19:00",
          "area": "新宿",
          "shopName": "和食処 ますだ",
          "budget": 5500,
          "paymentDest": "三菱UFJ銀行 〇〇支店 普通 1234567 マスダシュゾウ",
          "paypayLink": "https://paypay.me/xxxx/5500",
          "managerComment": "点数が一番高かったこの日程で予約しました！楽しみましょう。"
        }
      }
    }