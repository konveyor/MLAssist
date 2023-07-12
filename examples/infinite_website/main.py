from langchain import OpenAI, ConversationChain
from langchain import HuggingFacePipeline
from langchain.chat_models import ChatOpenAI
from flask import Flask, redirect, request
from dotenv import load_dotenv
import pickle
import os
import re

load_dotenv()

app = Flask(__name__)
llm = ChatOpenAI(temperature=0.9)


# llm = HuggingFacePipeline.from_model_id(
#     model_id="nomic-ai/gpt4all-j",
#     # model_id="bigscience/bloom-1b7",
#     task="text-generation",
#     model_kwargs={"temperature": 0.9, "max_length": 256},
# )

# from langchain.llms import GPT4All
# model_path = "models/ggml-gpt4all-j.bin"
# llm = GPT4All(model=model_path, n_ctx=1000, backend="gptj", verbose=False)

if os.path.exists("site.pickle"):
  with open('site.pickle', 'rb') as handle:
    db = pickle.load(handle)
else:
  db = {}

def clean_text(rgx_list, text):
  new_text = text
  for rgx_match in rgx_list:
    new_text = re.sub(rgx_match, '', new_text)
  return new_text

def generate_article(path):
  val = llm.predict(f"""
Generate a valid wikipedia-style article in html for the following url `https://en.wikipedia.org/{path}`.
Include a lot of href links to related topics within the text itself.
Include a "See Also" section at the end of the article.
""")

  val = re.sub(r"<style>[\s\S]*<\/style>", '', val)
  val = re.sub(r"https:\/\/en.wikipedia.org\/", '/', val)
  val = re.sub(r'style=\"[\s\S]*\"', '', val)
  val = re.sub(r"<head>", """
<head><style>
body {
  font-family: sans-serif;
  margin-left: auto;
  margin-right: auto;
  max-width: 80ch;
}

h1 {
  font-size: 28px;
  margin-bottom: 10px;
}

h2 {
  font-size: 24px;
  margin-bottom: 8px;
}

p {
  margin-bottom: 10px;
}

a {
  color: #0645ad;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

hr {
  border-bottom: 1px black;
}
</style>
""", val)

  val = re.sub(r"<body>", f"""
  <body>
  <form action="/{path}" method="post">
    <input type="submit" name="submit_button" value="🔃"/>
  </form>
  <hr>""", val)

  # <input type="text"   name="searchterm" />
  # <input type="submit" name="submit_button" value="🔎"/>

  db[path] = val
  with open('site.pickle', 'wb') as handle:
    pickle.dump(db, handle, protocol=pickle.HIGHEST_PROTOCOL)

  print(val)
  return val

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods = ['POST', 'GET'])
def wiki_page(path):
  if request.method == "POST":
    if request.form['submit_button'] == "🔃":
      if path in db:
        del db[path]
      
      redirect(path)
    else:

      redirect(f"/wiki/{request.form.get('searchterm')}")

  if path in db:
    print(db[path])
    return db[path]

  return generate_article(path)
  


if __name__ == "__main__":
  app.run()
