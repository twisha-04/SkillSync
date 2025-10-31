# chains/general_chain.py
from models.ChatGroq import get_chatgroq

llm = get_chatgroq()
response = llm.invoke("What are the top skills for a data scientist?")
print(response)
