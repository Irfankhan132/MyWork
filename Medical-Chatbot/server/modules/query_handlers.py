import re
from logger import logger

def query_chain(chain, user_input: str):
    try:
        logger.debug(f"Running chain for input: {user_input}")

        result = chain.invoke({"query": user_input})

        answer = result["result"]

        # Remove model thinking text like <think>...</think>
        answer = re.sub(
            r"<think>.*?</think>",
            "",
            answer,
            flags=re.DOTALL
        ).strip()

        response = {
            "response": answer,
            "sources": [
                doc.metadata.get("source", "")
                for doc in result["source_documents"]
            ]
        }

        logger.debug(f"Chain response: {response}")
        return response

    except Exception as e:
        logger.exception("Error on query chain")
        raise