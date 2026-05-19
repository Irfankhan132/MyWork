import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
PINECONE_ENV="us-east-1"
PINECONE_INDEX_NAME="medicalindex384"

os.environ["GOOGLE_API_KEY"]=GOOGLE_API_KEY

UPLOAD_DIR="./uploaded_docs"
os.makedirs(UPLOAD_DIR,exist_ok=True)


# initialize pinecone instance
pc=Pinecone(api_key=PINECONE_API_KEY)
spec=ServerlessSpec(cloud="aws",region=PINECONE_ENV)
existing_indexes = [i.name for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,
        metric="dotproduct",
        spec=spec
    )
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)


index=pc.Index(PINECONE_INDEX_NAME)

# load,split,embed and upsert pdf docs content

def load_vectorstore(uploaded_files):
    embed_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    file_paths = []

    for file in uploaded_files:
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        file_paths.append(str(save_path))

    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        # texts = [chunk.page_content for chunk in chunks]
        # metadatas = [chunk.metadata for chunk in chunks]
        # ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]

        texts = [chunk.page_content for chunk in chunks]

        metadatas = [
            {
                **chunk.metadata,
                "text": chunk.page_content
            }
            for chunk in chunks
        ]

        ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]

        # print(f"🔍 Embedding {len(texts)} chunks...")
        # embeddings = embed_model.embed_documents(texts)

        embeddings = []

        batch_size = 20

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            print(f"Processing batch {i//batch_size + 1}")

            batch_embeddings = embed_model.embed_documents(batch)

            embeddings.extend(batch_embeddings)

            time.sleep(5)

        # print("📤 Uploading to Pinecone...")
        # with tqdm(total=len(embeddings), desc="Upserting to Pinecone") as progress:
        #     index.upsert(vectors=zip(ids, embeddings, metadatas))
        #     progress.update(len(embeddings))

        # print(f"✅ Upload complete for {file_path}")

        print("Upserting embedding...")

        vectors = list(zip(ids, embeddings, metadatas))

        batch_size = 50

        with tqdm(total=len(vectors), desc="Upserting to Pinecone") as progress:
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch)
                progress.update(len(batch))
