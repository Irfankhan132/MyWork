from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from modules.llm import get_llm_chain
from modules.query_handlers import query_chain
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
from pydantic import Field
from typing import List, Optional
from logger import logger
import os
import time
from modules.evaluation_logger import save_evaluation_log

router=APIRouter()

def keyword_score(text: str, query: str) -> int:
    text = text.lower()
    keywords = query.lower().split()

    score = 0
    for word in keywords:
        if len(word) > 3 and word in text:
            score += 1

    return score

@router.post("/ask/")
async def ask_question(
    question:str=Form(...),
    username:str=Form(...),
    chat_history:str=Form("")
    ):
    try:
        logger.info(f"User query:{question}")
        start_time = time.time()
        
        # embed model + pinecone setup
        pc = Pinecone(api_key = os.environ["PINECONE_API_KEY"])
        index = pc.Index(os.environ["PINECONE_INDEX_NAME"])
        embed_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        search_query = f"""
        Conversation history:
        {chat_history}

        Current question:
        {question}
        """

        embedded_query = embed_model.embed_query(search_query)

        res = index.query(
            vector=embedded_query,
            top_k=20,
            include_metadata=True,
            filter={"user_id": username}
        )
        
        print("Pinecone result:", res)
        print("Matches count:", len(res["matches"]))

        for match in res["matches"]:
            print("Score:", match["score"])
            print("Metadata:", match["metadata"])
        
        docs = []

        for match in res["matches"]:
            text = match["metadata"].get("text", "")
            metadata = match["metadata"]

            vector_score = match.get("score", 0)
            keyword_match_score = keyword_score(text, question)

            metadata["vector_score"] = vector_score
            metadata["keyword_score"] = keyword_match_score
            metadata["hybrid_score"] = vector_score + (0.1 * keyword_match_score)

            docs.append(
                Document(
                    page_content=text,
                    metadata=metadata
                )
            )

        docs = sorted(
            docs,
            key=lambda doc: doc.metadata.get("hybrid_score", 0),
            reverse=True
        )
        
        # Keep only best reranked chunks
        docs = docs[:5]

        print("\n===== RERANKED RESULTS =====")

        for i, doc in enumerate(docs, start=1):
            print(
                f"Rank {i} | "
                f"Hybrid Score: {doc.metadata['hybrid_score']:.4f} | "
                f"Page: {doc.metadata.get('page')}"
            )
        
        class SimpleRetriever(BaseRetriever):
            tags: Optional[List[str]] = Field(default_factory=list)
            metadata: Optional[dict] = Field(default_factory=dict)

            def __init__(self, documents: List[Document]):
                super().__init__()
                self._docs = documents

            def _get_relevant_documents(self, query: str) -> List[Document]:
                return self._docs

        retriever = SimpleRetriever(docs)
        chain = get_llm_chain(retriever)
        full_question = f"""
        Previous conversation history:
        {chat_history}
        Current question:
        {question}
        """
        result = query_chain(chain, full_question)
        
        response_time = time.time() - start_time
        sources = [
            {
                "source": doc.metadata.get("source", ""),
                "page": doc.metadata.get("page", ""),
                "hybrid_score": doc.metadata.get("hybrid_score", 0)
            }
            for doc in docs
        ]
        
        save_evaluation_log(
            username=username,
            question=question,
            response_time=response_time,
            sources=sources,
            retrieved_chunks=len(docs)
        )

        logger.info("query successful")
        return result
        
        
        
    except Exception as e:
        logger.exception("Error processing question")
        return JSONResponse(status_code = 500, content = {"error": str(e)})