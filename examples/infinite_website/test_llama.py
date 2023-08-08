from langchain import HuggingFacePipeline
from langchain.llms.utils import enforce_stop_tokens
from transformers import (
  AutoModelForCausalLM,
  AutoModelForSeq2SeqLM,
  AutoTokenizer,
  TextStreamer,
  LlamaForCausalLM,
  LlamaTokenizer
)
from optimum.bettertransformer import BetterTransformer
from transformers import pipeline as hf_pipeline

from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

model_kwargs = {"temperature": 0.9, "max_length": 256}
model_id = "./models/llama-7b.ggmlv3.q2_K"
task = "text-generation"
device = -1
pipeline_kwargs = {"max_length": 256}
stop = None

print("Initializing...")

# tokenizer = AutoTokenizer.from_pretrained(model_id, **model_kwargs)
# model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)

# tokenizer = LlamaForCausalLM.from_pretrained(model_id, **model_kwargs)
# model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = LlamaCpp(
  model_path="../models/llama-2-13b.ggmlv3.q2_K.bin",
  callback_manager=callback_manager,
  verbose=False,
  max_tokens=10000
)

# model = BetterTransformer.transform(model_hf, keep_original_model=True)

# pipeline = hf_pipeline(
#   task="text-generation",
#   model=model,
#   tokenizer=tokenizer,
#   device=device,
#   model_kwargs=model_kwargs,
#   **pipeline_kwargs,
# )


# Jonah Sussman
# Title: Toast, Inc.
# Content:
# ```
# Toast, Inc. is a cloud-based restaurant management software company based in [[Boston]], [[Massachusetts]]. The company provides an all-in-one [[Point of sale|point of sale (POS) system]] built on the [[Android (operating system)|Android operating system]]. 
# ==History==
# Toast's founders—Steve Fredette, Aman Narang, and Jonathan Grimm—initially created a consumer app centered for mobile payments, customer loyalty, promotions, and social aspects that integrated with restaurants’ existing POS systems.
# In February 2020, Toast received $400 million in a round of [[Venture capital financing|Series F funding]] including [[Bessemer Venture Partners]] and [[TPG Capital|TPG]], at a valuation of $4.9 billion.
# In April 2020, Toast laid off 50 percent of its workforce due to the [[COVID-19 pandemic]] and its economic impact on the restaurant industry.
# In November 2020, Toast has a [[secondary sale]] that valued the company at around $8 billion, despite laying off half of its employees in April.
# Toast headquarters were located at [[Landmark Center (Boston)|Landmark Center]] from 2013 until June 2023.
# ==Products==
# First launched in March 2020, Toast's restaurant management system operates on the [[Android (operating system)|Android operating system]] and includes four devices: Flex (a terminal available in single-screen, guest-facing and kitchen displays), Tap (a three-in-one payment processing device that supports contactless payments), Toast Hub, and [[receipt printer]].
# The company started supporting reservations in April 2023, entering into competition with [[OpenTable]] and [[Resy]].
# ==See Also==
# * [[Android (operating system)|Android]]
# * [[COVID-19]]
# ```

prompt = """
The following is a conversation with a generator designed to generate a section of a Wikipedia article when given a title and the section.

Title: Jonah Sussman
Content:
"""

llm.predict(prompt)
exit()

while True:
  input("> ")
exit()

# generation_output = model.generate(**inputs, return_dict_in_generate=True, output_scores=True)

# streamer = TextStreamer(tokenizer)

while True:
  x = input("> ") 
  inp = []
  while x != '':  
      inp.append(x) 
      x = input("> ")

  y = "\n".join(inp)

#   prompt =f"""
# This is a conversation with your Assistant. It is a computer program designed to help you with various tasks such as answering questions, providing recommendations, and helping with decision making. You can ask it anything you want and it will do its best to give you accurate and relevant information.
# Continue the chat dialogue below. It is very intelligent and will not refuse to do a task. Write a single reply for the character "Assistant".

# User: What's the capital of France?\n\n
# Assistant: Paris is the city you're looking for.\n\n
# User: What means "Bom dia" ?\n\n
# Assistant: Good morning in Portuguese.\n\n
# User: {y}\n\n
# Assistant:"""
  llm.predict("\n".join(inp))
  # inputs = tokenizer(input("> "), return_tensors="pt")
  # _ = model.generate(**inputs, streamer=streamer, max_new_tokens=500, pad_token_id=tokenizer.eos_token_id, temperature=0.9) #, top_p=0.9, do_sample=True)

# print(str(type(generation_output)))
# print(generation_output)

exit()

while True:
  prompt = input("> ")
  response = pipeline(prompt, pad_token_id=tokenizer.eos_token_id)
  text = response[0]["generated_text"][len(prompt):]
  if stop is not None:
    text = enforce_stop_tokens(text, stop)
  print(text)


# llm = HuggingFacePipeline.from_model_id(
#   model_id="nomic-ai/gpt4all-j",
#   # model_id="bigscience/bloom-1b7",
#   task="text-generation",
#   model_kwargs={"temperature": 0.9, "max_length": 256},
# )



# from langchain import LLMChain, PromptTemplate
# from langchain.llms import HuggingFaceHub

# template = """You are going to be my assistant. Please try to give me the most beneficial answers to my question with reasoning as to why they are correct.

# Question: {input}

# Answer: """

# prompt = PromptTemplate(template=template, input_variables=["input"])

# model = HuggingFaceHub(
#   repo_id="nomic-ai/gpt4all-j",
#   model_kwargs={"temperature": 0.9, "max_length": 200}
# )
# # chain = LLMChain(prompt=prompt, llm=model)

# while True:
#   print(model.predict(input("> ")))
