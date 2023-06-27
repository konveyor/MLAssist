from dotenv import load_dotenv
from langchain.llms import OpenAI

# Make sure to set OPEN_API_KEY in .env
load_dotenv()

llm = OpenAI(temperature=0.9)

while True:
  s = input("> ")
  r = llm.predict(s)
  print(r) 