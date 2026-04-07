from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(path="C:/Users/navee/PycharmProjects/AI_AUTOMATION/data/sample_docs.md"):
    loader = TextLoader(path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n##", "\n#", "\n"]
    )
    chunks = splitter.split_documents(documents)

    print(f"[DEBUG] Loaded {len(documents)} document(s), {len(chunks)} chunks")
    for i, c in enumerate(chunks[:2]):
        print(f"[DEBUG] Chunk {i+1} preview:\n{c.page_content[:200]}\n{'-'*50}")

    return chunks

_retriever = None

def build_retriever():
    global _retriever
    if _retriever is None:
        chunks = load_documents()
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vectorstore = FAISS.from_documents(chunks, embeddings)
        _retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    return _retriever