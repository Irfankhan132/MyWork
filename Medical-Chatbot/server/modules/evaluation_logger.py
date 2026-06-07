from database import SessionLocal
from models import EvaluationLog
from datetime import datetime


def save_evaluation_log(
    username,
    question,
    response_time,
    sources,
    retrieved_chunks
):
    db = SessionLocal()

    try:
        log = EvaluationLog(
            username=username,
            question=question,
            response_time_seconds=round(response_time, 2),
            retrieved_chunks=retrieved_chunks,
            sources=str(sources),
            created_at=datetime.utcnow()
        )

        db.add(log)
        db.commit()

    finally:
        db.close()


def get_evaluation_logs(username=None):

    db = SessionLocal()

    try:

        query = db.query(EvaluationLog)

        if username:
            query = query.filter(
                EvaluationLog.username == username
            )

        logs = query.order_by(
            EvaluationLog.created_at.desc()
        ).all()

        return [
            {
                "timestamp": log.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "username": log.username,
                "question": log.question,
                "response_time_seconds": log.response_time_seconds,
                "retrieved_chunks": log.retrieved_chunks,
                "sources": log.sources
            }
            for log in logs
        ]

    finally:
        db.close()