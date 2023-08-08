from langchain.embeddings import OpenAIEmbeddings, LlamaCppEmbeddings
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain.agents import tool
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

from chromadb.config import Settings

import os
import sys
import argparse
import httpx
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

CHROMA_SETTINGS = Settings(
  chroma_db_impl='duckdb+parquet',
  persist_directory="chroma_persist",
  anonymized_telemetry=False
)

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = ChatOpenAI(temperature=0.0)

@tool
def get_word_length(word: str) -> int:
  """Returns the length of a word."""
  return len(word)

@tool
def tree_string(path, indentation='  ', show_files=True):
  """Returns all directories and subdirectories of a given directory"""
  tree = ''
  if not os.path.exists(path):
    return f"Path '{path}' does not exist."

  def explore_directory(current_path, depth):
    nonlocal tree
    files = []
    dirs = []
    with os.scandir(current_path) as entries:
      for entry in entries:
        if entry.is_dir():
          dirs.append(entry.name)
        elif show_files:
          files.append(entry.name)
    dirs.sort()
    files.sort()

    for d in dirs:
      tree += f"{indentation * depth}{d}\n"
      explore_directory(os.path.join(current_path, d), depth + 1)
    if show_files:
      for f in files:
        tree += f"{indentation * depth}{f}\n"

  tree += path + '\n'
  explore_directory(path, 1)
  return tree

@tool
def get_summary(file_path):
  """Gets a short summary of the given file. Note: this is not a substitute for looking at the actual contents of the file."""
  llm = ChatOpenAI(temperature=0)
  prompt = f"""
    You are a hyperintelligent software engineer.
    Summarize the following code. Please be extremely consise.
    {read_file_to_string(file_path)}
  """
  return llm.predict(prompt)
  # chain = load_summarize_chain(llm, chain_type="map_reduce")
  # return chain.run([Document(page_content=read_file_to_string(file_path))])

@tool
def read_file_to_string(file_path):
  """Takes a file's location as input and prints out the contents of the file"""
  try:
    with open(file_path, 'r') as file:
      file_contents = file.read()
      return file_contents
  except FileNotFoundError:
    return f"File '{file_path}' not found."
  except IOError:
    return f"Error reading file '{file_path}'."
  
@tool
def search_wikipedia(q):
  """Returns a summary from searching Wikipedia"""
  return httpx.get("https://en.wikipedia.org/w/api.php", params={
    "action": "query",
    "list": "search",
    "srsearch": q,
    "format": "json"
  }).json()["query"]["search"][0]["snippet"]

@tool
def eval_python(what):
  """Runs a calculation and returns the result - uses Python so be sure to use floating point syntax if necessary"""
  return eval(what)


tools = [tree_string, read_file_to_string, search_wikipedia, eval_python]
# tools = [tree_string, read_file_to_string, get_summary]

# system_message = SystemMessage(content="You are very powerful assistant that helps when migrating applications to Kubernetes.")
system_message = SystemMessage(content="You are very powerful assistant.")

MEMORY_KEY = "chat_history"
prompt = OpenAIFunctionsAgent.create_prompt(
  system_message=system_message,
  extra_prompt_messages=[MessagesPlaceholder(variable_name=MEMORY_KEY)]
)

memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)
agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

# agent_executor.run("")
# The git repository for 'example-1' is located in the folder 'example-1'. Please determine if there would be any pain points in migrating this application.
# The git repository for 'petclinic' is located in the folder 'petclinic-src'. Please determine if there would be any pain points in migrating this application. Examine the contents of files if need be.

while True:
  agent_executor.run(input("> "))