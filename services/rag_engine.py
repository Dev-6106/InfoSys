import os
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import TextLoader, PyPDFLoader

DOCS_PATH = Path("./rag_docs")
INDEX_PATH = Path("./faiss_index")
EMBED_MODEL = "models/gemini-embedding-001"
CHAT_MODEL = "gemini-1.5-pro"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 4

def load_documents():
    docs = []
    for p in DOCS_PATH.glob("**/*"):
        if p.suffix.lower() in {".txt", ".md"}:
            docs.extend(TextLoader(str(p)).load())
        elif p.suffix.lower() == ".pdf":
            docs.extend(PyPDFLoader(str(p)).load())
    return docs

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(docs)

def build_or_load_index(rebuild=False):
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)

    if rebuild or not INDEX_PATH.exists():
        docs = load_documents()
        chunks = split_documents(docs)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        INDEX_PATH.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(INDEX_PATH))
        return vectorstore

    return FAISS.load_local(str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True)

def make_rag_chain():
    vectorstore = build_or_load_index()
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": TOP_K})
    prompt = """
    You are a precise assistant. Answer based only on the provided context.
    If the answer is not in the context, say "I don't know".
    Cite sources where applicable.

    Context: {context}
    Question: {input}
    """

    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0.2)
    doc_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, doc_chain)
    return rag_chain

def answer_query(query: str):
    rag = make_rag_chain()
    result = rag.invoke({"input": query})
    return result.get("answer") or result.get("output") or "No answer found."
