from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="openrouter/free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)