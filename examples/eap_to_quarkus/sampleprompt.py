import os
from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import openai

_ = load_dotenv(find_dotenv()) 
openai.api_key = os.environ['OPENAI_API_KEY']
chat = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo")

temp ="""
You have been provided with prior solved examples in {text}. It is time to resolve a similar incident. Find a solution for the issue in {java_code_snippet}.
Make sure it is compatible with Quarkus 3.4.1 as well as Jakarta EE 9 and Java 11.

Make sure the output is displayed in the diff format like github
"""

prompt_template = ChatPromptTemplate.from_template(temp)

modernize_text = """
You are an expert in Java EAP and Quarkus technologies. You are going to assist with modernizing EAP applications to  
Quarkus 3.4.1, Jakarta EE 9, and Java 11. There are some sample scenarios provided below,

Example 1:
Incident metdata: Stateless scoped bean

Issue details:

@Stateless
public class OrderService {
  // ...
}

Resolution:

@ApplicationScoped
public class OrderService {
 // ...
}

Example 2:
Incident metdata: Stateless scoped bean

Issue details:

@Stateless
public class CatalogService {
    // ...
}

Resolution:

@ApplicationScoped
public class CatalogService {
    // ...
}
"""

modernize_question="""
Incident metadata: Stateless scoped bean

Issue details:
```
@Stateless
public class MemberRegistration {
 '....'
 '....'
}
```
"""

modernize_messages = prompt_template.format_messages(
                    text=modernize_text,
                    java_code_snippet=modernize_question)

modernize_response = chat(modernize_messages)

print(modernize_response.content)