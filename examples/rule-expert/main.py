import os
import sys
import yaml
import time
import utils
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from prompts import PromptType, get_prompt


def _main():
    key = os.environ.get("OPENAI_KEY", "")
    if not key:
        print("env OPENAI_KEY required")
        sys.exit(1)

    model = ChatOpenAI(openai_api_key=key)

    # STEP 1: Ask LLM to summarize a release note for us
    # given a release note, identify all lines that either indicate a deprecation or removal of an API
    release_note_reader_prompt = get_prompt(PromptType.ReleaseNoteItemGen,
                                            utils.get_few_shot_examples(PromptType.ReleaseNoteItemGen))
    release_note_reader_chain = release_note_reader_prompt | model | StrOutputParser()
    # pick a test-case containing contents of a release note
    tc = utils.get_test_cases(PromptType.ReleaseNoteItemGen)[0]
    print("[1/3] Reading the release note...")
    # invoke LLM to get the identified deprecation/removal items
    release_note_reader_output = release_note_reader_chain.invoke(tc)
    # split the output into distinct items
    release_note_items = utils.parse_prompt_output(
        PromptType.ReleaseNoteItemGen, release_note_reader_output)

    # STEP 2: Generate just the search patterns from summarized items
    print("[2/3] Generating search queries for identified removed / deprecated APIs...")
    queries: list[dict] = []
    # for each item we identified from release note, generate a simple search query
    for idx, item in enumerate(release_note_items):
        time.sleep(2)
        search_query_gen_prompt = get_prompt(PromptType.SearchQueryGen,
                                             utils.get_few_shot_examples(PromptType.SearchQueryGen))
        search_query_gen_chain = search_query_gen_prompt | model | StrOutputParser()
        output = search_query_gen_chain.invoke({"input": item})
        queries.append({
            "message": item,
            "query": output,
        })
        print("\t[{}/{}] Generated query for note item {}".format(idx +
              1, len(release_note_items), item))

    # STEP 3: Generate an actual when block for a rule using the search query
    print("[3/3] Generating 'when' blocks from search queries...")
    rules: list[dict] = []
    # given an LLM generated search query, convert it into a when block
    for idx, query in enumerate(queries):
        time.sleep(2)
        when_block_gen_prompt = get_prompt(PromptType.WhenBlockGen,
                                           utils.get_few_shot_examples(PromptType.WhenBlockGen))
        when_block_gen_chain = when_block_gen_prompt | model | StrOutputParser()
        output = when_block_gen_chain.invoke({
            "input": query["query"],
            "language": tc["language"],
        })
        rules.append({
            "when": output,
            "message": query["message"],
        })
        print("\t[{}/{}] Generated 'when' block for query {}".format(idx +
              1, len(queries), query["query"]))

    with open("output_raw.yaml", "w") as f:
        yaml.safe_dump(rules, f)

    sanitized_rules: list[dict] = []
    for rule in rules:
        msg: str = rule.get("message", "")
        when: str = rule.get("when", "")
        msg = msg.replace("- ", "", 1)
        when = when.replace("```yaml", "", 1)
        when = when.replace("```", "", 1)
        when_dict = {}
        try:
            when_dict = yaml.safe_load(when)
        except:
            pass
        when_dict = when_dict.get("when", {})
        if msg and when_dict:
            sanitized_rules.append({
                "message": msg,
                "when": when_dict,
            })

    with open("output_rules.yaml", "w") as f:
        yaml.dump(sanitized_rules, f, default_flow_style=False)

    print("[DONE] Generated output in output_rules.yaml")


if __name__ == "__main__":
    _main()
