from dotenv import load_dotenv
from langchain.llms import OpenAI

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
  AIMessage,
  HumanMessage,
  SystemMessage
)

import argparse
import sys

# Make sure to set OPEN_API_KEY in .env
load_dotenv()

parser = argparse.ArgumentParser("simple-summarizer")
parser.add_argument("-f", "--file", help="The file to summarize.")
args = parser.parse_args()

# Try to read the file's content into file_content
file_content = ""
try:
  with open(args.file, 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines, start=1):
      file_content += f"{str(i).rjust(6, '0')} {line}"
except FileNotFoundError:
  sys.stderr.write("Please supply a filename with the flag '--file' or '-f'.")
  exit()
except IOError:
  sys.stderr.write("Error reading the file.")
  exit()

# Use the LLM to summarize the code
llm = OpenAI(temperature=0)

prompt = f"""
Please summarize the following code. Make specific references to lines of code using the format "[000000]".
--- begin {args.file} ---
{file_content}
--- end {args.file} ---
"""

# prompt = f"""
# Please make a diagram for the following code in mermaid.js. Use the line numbers instead of the content of each line.
# --- begin {args.file} ---
# {file_content}
# --- end {args.file} ---
# """

print("PROMPT")
print(prompt)
print("RESULT")
result = llm.predict(prompt)
print(result)