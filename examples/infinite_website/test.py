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

model_kwargs = {"temperature": 0.9, "max_length": 256}
model_id = "./models/llama-7b.ggmlv3.q2_K"
task = "text-generation"
device = -1
pipeline_kwargs = {"max_length": 256}
stop = None

print("Initializing...")

# tokenizer = AutoTokenizer.from_pretrained(model_id, **model_kwargs)
# model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)

tokenizer = LlamaForCausalLM.from_pretrained(model_id, **model_kwargs)
model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)

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





# generation_output = model.generate(**inputs, return_dict_in_generate=True, output_scores=True)

streamer = TextStreamer(tokenizer)

while True:
  inputs = tokenizer(input("> "), return_tensors="pt")
  _ = model.generate(**inputs, streamer=streamer, max_new_tokens=500, pad_token_id=tokenizer.eos_token_id, temperature=0.9) #, top_p=0.9, do_sample=True)

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
