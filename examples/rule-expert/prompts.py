from enum import Enum

from langchain.prompts import (AIMessagePromptTemplate, ChatPromptTemplate,
                               FewShotChatMessagePromptTemplate,
                               HumanMessagePromptTemplate)
from langchain.prompts.example_selector.base import BaseExampleSelector
from langchain.schema import SystemMessage

PromptType = Enum("PromptType", [
    "ReleaseNoteItemGen",
    "SearchQueryGen",
    "WhenBlockGen",
])


def get_prompt(pType: PromptType, few_shot_examples: list[dict], selector: BaseExampleSelector = None) -> ChatPromptTemplate:
    """
    Returns a prompt for given PromptType
    """
    if not few_shot_examples:
        raise Exception("at least one example needed")

    return {
        PromptType.ReleaseNoteItemGen: _get_release_note_item_gen_prompt,
        PromptType.SearchQueryGen: _get_search_query_gen_prompt,
        PromptType.WhenBlockGen: _get_when_block_gen_prompt,
    }[pType](few_shot_examples=few_shot_examples, selector=selector)


def _get_simple_few_shot_example_prompt(examples: list[dict], selector: BaseExampleSelector = None) -> ChatPromptTemplate:
    """
    Returns a chat prompt containing few shot examples with templates - input and output
    """
    few_shot_example = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template("{input}"),
        AIMessagePromptTemplate.from_template("{output}")
    ])
    return FewShotChatMessagePromptTemplate(
        example_prompt=few_shot_example,
        examples=examples,
        example_selector=selector,
    )


def _get_release_note_item_gen_prompt(few_shot_examples: list[dict], selector: BaseExampleSelector = None) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        SystemMessage(content="""
            You're an expert programmer. The user is reading a release note. 
            They want to find the content in the release note that indicates an API deprecation or API removal.
            Help the user find this information from a given release note.
            """),
        _get_simple_few_shot_example_prompt(few_shot_examples, selector),
        HumanMessagePromptTemplate.from_template("""
            Identify items in the following content that indicate either API removals or deprecations:
            ```
            {input}
            ```
            Return each unique deprecation / removal item on a newline with - character at the beginning.
            Sometimes a note for an API can be multi-line. Identify such lines and group them correctly into one item.
            Sometimes a note item can also mention alternatives for the removed / deprecated API. Include this information in the line as well.
            Include wording in each item to clearly indicate whether its a removal or deprecation.
            """)
    ])


def _get_search_query_gen_prompt(few_shot_examples: list[dict], selector: BaseExampleSelector = None) -> ChatPromptTemplate:
    """
    Returns a prompt that asks LLM to convert a release note item into a search query
    """
    return ChatPromptTemplate.from_messages([
        SystemMessage(content="""
            You're an expert programmer. The user is using a source code analysis tool that takes a search query, and returns matches for the search query in the source code. 
            The search query is defined by a regex pattern. The tool finds references of that pattern in the source code. 
            For example, in a Java application, to find references to packages within the org.jbpm group, a search query can be written as `org.jbpm.*`. 
            The query pattern can contain wildcard `*` to match anything, and a group like `(package1|package2)` to match any one of the grouped strings. 
            Logical AND and OR can be performed on multiple search queries like `org.jbpm.* OR org.jbpm.sub-package*` or `langchain.chains* AND langchain.prompts*` to form a single complex query.
            The user wants to write search queries to find deprecations and removals in Python APIs from the natural language description of the changes. 
            Help user generate search queries for a source code analysis tool."""),
        _get_simple_few_shot_example_prompt(few_shot_examples, selector),
        HumanMessagePromptTemplate.from_template("""Generate a query from following description of a deprecated or removed api:
            ```
            {input}
            ```
            Only return the query.
            """),
    ])


def _get_when_block_gen_prompt(few_shot_examples: list[dict], selector: BaseExampleSelector = None) -> ChatPromptTemplate:
    few_shot_examples_in_simple_format = []
    for example in few_shot_examples:
        if "language" in example:
            few_shot_examples_in_simple_format.append({
                "input": "Create a {language} condition from query - '{{input}}'".format(language=example["language"]),
                "output": "{output}"
            })
    return ChatPromptTemplate.from_messages([
        SystemMessage(content="""
            You're an expert programmer. The user is trying to create a YAML rule from a search query. A search query is a regex pattern.
            A rule is written for a specific language and a query. In general, for a language "X" and a query "Y", a rule is written as:
            ```yaml
            when:
              X.referenced:
                pattern: Y
            ```
            Logical AND and OR operation can be performed on multiple queries to form one complex query. For example, "Q1 AND Q2" is a single query formed by performing a logical AND operation between results of sub-queries Q1 and Q2. 
            The rule format provides "and" and "or" fields to express such a query. These fields take a list of all sub-queries.
            For example, if a query is 'Q1 AND Q2' and language is 'java', the rule is written as:
            ```yaml
            when:
              and:
              - java.referenced:
                  pattern: Q1
              - java.referenced:
                  pattern: Q2
            ```
            Similarly, for a query 'Q1 OR Q2' and language is 'python', the rule is written as:
            ```yaml
            when:
              or:
              - python.referenced:
                  pattern: Q1
              - python.referenced:
                  pattern: Q2
            ```
            Note that queries Q1, Q2 above are just examples, and actual queries will be different.
            Help the user generate such queries from their input.
            """),
        _get_simple_few_shot_example_prompt(
            few_shot_examples_in_simple_format, selector),
        HumanMessagePromptTemplate.from_template("""
            Create a {language} condition from query - '{input}'
            Only output the final rule.
            """)
    ])
