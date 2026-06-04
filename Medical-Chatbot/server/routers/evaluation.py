from fastapi import APIRouter, Query
from modules.evaluation_logger import get_evaluation_logs

router = APIRouter()


@router.get("/evaluation/")
async def get_evaluation_data(username: str = Query(...)):
    logs = get_evaluation_logs()

    user_logs = [
        log for log in logs
        if log.get("username") == username
    ]

    total_queries = len(user_logs)

    avg_response_time = 0
    if user_logs:
        avg_response_time = sum(
            log.get("response_time_seconds", 0)
            for log in user_logs
        ) / len(user_logs)

    return {
        "username": username,
        "total_queries": total_queries,
        "average_response_time": round(avg_response_time, 2),
        "logs": user_logs
    }