from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_llm_chain(retriever):
    llm = ChatGroq(
        groq_api_key = GROQ_API_KEY,
        model_name = "qwen/qwen3-32b"
    )
    
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        You are MediBot, an AI medical document assistant.

        You must use BOTH:
        1. Previous conversation
        2. Retrieved document context

        to answer the current question.

        If the current question contains words like:
        - it
        - its
        - they
        - them
        - this condition

        then use the previous conversation to understand what the user means.

        Previous Conversation:
        {question}

        Retrieved Context:
        {context}

        Instructions:
        - Give a clear and concise answer.
        - Use previous conversation context for follow-up questions.
        - If the answer is not found in the documents, say:
        "I could not find relevant information in the uploaded documents."
        - Do not give diagnosis or personal medical advice.
        - Do not generate fake information.
        - Do not include  <thinks> tags.

        Answer:
        """
    )
    
    return RetrievalQA.from_chain_type(
        llm = llm,
        chain_type = "stuff",
        retriever = retriever,
        chain_type_kwargs = {"prompt":prompt},
        return_source_documents = True
    )