from fastapi import APIRouter, Depends, HTTPException
from modules.evaluation_logger import get_evaluation_logs
from security import get_current_user

router = APIRouter()


@router.get("/evaluation/")
async def get_evaluation_data(
    username: str = Depends(get_current_user)
):
    user_logs = get_evaluation_logs(username)
    
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

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