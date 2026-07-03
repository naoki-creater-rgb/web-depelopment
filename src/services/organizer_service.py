from repositories.candidate_repository import EventCandidateRepository
from repositories.event_repository import EventRepository

from datetime import datetime

class OrganizerService:
  @staticmethod
  def createNewEvent(manager_id, event_name, response_deadline, description, candidate_areas: list[str], candidate_dates: list[str]):
    """
    新しいイベントを登録する
    """
    #TODO:EventRepositoryクラスのcreateEvent(manager_id, event_name, response_deadline, description)を呼び出し、変数に返却された値（Eventオブジェクト）を代入する
    #TODO:EventCandidateRepositoryクラスのbulkInsertAreaCandidates(event_id, candidate_areas)を呼び出す。event_idは上の工程で取得したEventオブジェクトから取得する。
    #TODO:EventCandidateRepositoryクラスのbulkInsertDateCandidates(event_id, candidate_dates)を呼び出す。event_idは上の工程で取得したEventオブジェクトから取得する。
    #TODO:返却値を生成し、返却する
    try:
      created_event = EventRepository.createEvent(manager_id, event_name, datetime.strptime(response_deadline, "%Y-%m-%d %H:%M"), description)
      candidate_areas = EventCandidateRepository.bulkInsertAreaCandidates(created_event.event_id, candidate_areas)
      candidate_dates = EventCandidateRepository.bulkInsertDateCandidates(created_event.event_id, candidate_dates)

      return {
        "status": "success",
        "data": {
          "eventId": created_event.event_id,
          "eventName": created_event.event_name,
          "deadlineForResponses": created_event.response_deadline,
          "managerId": created_event.manager_id,
          "description": created_event.description,
          "status": "検討中",
          "candidateDates": [
            { "id": 1, "datetime": "2026-04-01 19:00", "totalScore": 0 },
            { "id": 2, "datetime": "2026-04-02 19:00", "totalScore": 0 }
          ],
          "candidateAreas": [
            {"area_id": 1, "area": "新宿"},
            {"area_id": 2, "area": "渋谷"},
            {"area_id": 3, "area": "池袋"}
          ]
        }
      }
      
    except Exception:
      return {
        "status": "failed",
        "message": "イベントの登録に失敗しました"
      } 
  
  @staticmethod
  def inviteUsers(event_id, user_ids: list[str]):
    """
    イベントにユーザを招待する
    """
    #TODO:EventParticipantRepositoryクラスのbulkInsertParticipants(event_id, user_ids)を呼び出し、返却された値を変数に代入する
    #TODO:返却値を作成し、返却する
    return {
      "status": "success",
      "data": {
        "invitedUsers": [
          { "userId": "user_002", "userName": "佐藤 花子" },
          { "userId": "user_003", "userName": "鈴木 一郎" }
        ],
        "event": {
          "eventId": 101,
          "eventName": "新年会2026"
        }
      }
    }
  
  @staticmethod
  def getManagedEvents(manager_id):
    """
    ユーザが管理しているイベントを取得する
    """
    #TODO:EventRepositoryクラスのfindEventsByParticipantId(manager_id)を呼び出し、返却値を代入する
    #TODO:返却値を作成し、返却する
    return {
      "status": "success",
      "data": {
        "underConsideration": [
          {
            "eventId": 101,
            "eventName": "新年会2026",
            "status": "検討中",
            "deadlineForResponses": "2026-02-27 15:00"
          }
        ],
        "confirmed": [
          {
            "eventId": 103,
            "eventName": "プロジェクト打ち上げ",
            "datetime": "2025-12-15 18:30",
            "status": "情報確定"
          }
        ],
        "alreadyHeld": [
          {
            "eventId": 100,
            "eventName": "忘年会2025",
            "status": "開催済み",
            "datetime": "2025-12-20 18:30",
            "shopName": "居酒屋 魚民"
          }
        ]
      }
    }
  
  @staticmethod
  def getEventDetail(event_id):
    """
    イベントの詳細を取得する
    """
    #TODO:EventRepositoryクラスのfindEventDetailById(event_id)を呼び出し、値を変数に代入する
    #TODO:返却値を作成し、返却する
    return {
      "status": "success",
      "data": {
        "eventId": 101,
        "eventName": "新年会2026",
        "deadlineForResponses": "2026-02-27 15:00",
        "totalParticipants": 8,
        "replyCount": 6,
        
        "dateSummaries": [
          {
            "dateCandidateId": 1,
            "datetime": "2026-04-01 19:00",
            "totalScore": 25,
            "details": { "5点": 4, "3点": 1, "0点": 1 }
          },
          {
            "dateCandidateId": 2,
            "datetime": "2026-04-05 18:30",
            "totalScore": 18,
            "details": { "5点": 2, "3点": 2, "0点": 2 }
          }
        ],

        "areaPreferences": [
          {"area_id":1, "area": "新宿", "count": 4 },
          {"area_id":2, "area": "渋谷", "count": 2 }
        ],

        "budgetSummary": {
          "average": 5500,
          "min": 4000,
          "max": 8000
        },

        "participantResponses": [
          {
            "userId": "user_001",
            "userName": "田中 太郎",
            "preferredBudget": 5000,
            "preferredArea": "新宿",
            "overallComment": "楽しみにしてます！禁煙席だと嬉しいです。",
            "dateResponses": [
              { "dateCandidateId": 1, "score": 5, "comment": "いつでもOK" },
              { "dateCandidateId": 2, "score": 0, "comment": "この日は出張" }
            ]
          }
        ],
        
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
  
  @staticmethod
  def confirmEvent(event_id, confirmed_area_id, confirmed_shop_name, confirmed_budget, confirmed_datetime_id, payment_destination, paypay_link = None):
    """
    イベント情報を確定する
    """
    #TODO:EventRepositoryクラスのupdateEventAsConfirmed(event_id, confirmed_area_id, confirmed_shop_name, confirmed_budget, confirmed_datetime_id, payment_destination, paypay_link)メソッドを呼び出し、値を変数に代入する
    #TODO:返却値を作成し、返却する
    return {
      "status": "success",
      "message": "イベントを確定しました。参加者に詳細情報が公開されます。",
      "data": {
        "eventId": 101,
        "eventName": "新年会2026",
        "deadlineForResponses": "2026-02-27 15:00",
        "status": "確定済み",
        "managerId": "user_001",
        "updatedAt": "2026-03-01T16:45:00Z",
        
        "confirmedDetails": {
          "datetime": "2026-04-01 19:00",
          "area": "新宿",
          "shopName": "和食処 ますだ",
          "budget": 5500,
          "paymentDest": "三菱UFJ銀行 〇〇支店 普通 1234567 マスダシュゾウ",
          "paypayLink": "https://paypay.me/xxxx/5500",
          "managerComment": "点数が一番高かったこの日程で予約しました！楽しみましょう。"
        },
        
        "summary": {
          "totalParticipants": 8,
          "replyCount": 8
        }
      }
    }