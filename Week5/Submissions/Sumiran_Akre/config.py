import os
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from tools import research_tools, review_tools

load_dotenv()

groq_model = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
groq_model_2 = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

chat_model = ChatGroq(model=groq_model_2)

research_model = ChatGroq(model=groq_model)
research_model_with_tools = research_model.bind_tools(research_tools)

writing_model = ChatGroq(model=groq_model)

review_model = ChatGroq(model=groq_model_2)
review_model_with_tools = review_model.bind_tools(review_tools)