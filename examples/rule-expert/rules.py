import logging
from glob import iglob
from os.path import join

from prompts import PromptType
from yaml import safe_load


def get_when(rule: dict) -> dict: return rule.get("when", {})
def get_message(rule: dict) -> dict: return rule.get("message", "")
def get_id(rule: dict) -> dict: return rule.get("ruleID", "")


def has_nested_condition(rule: dict) -> bool: return True if \
    get_when(rule).get("and", {}) != {} or \
    get_when(rule).get("or", {}) != {} else False


def load_yaml(path: str) -> any:
    with open(path, "r") as f:
        return safe_load(f)


def load_rules(path: str) -> list[dict]:
    all_rules = []
    for file in iglob(join(path, "**/*.yaml"), recursive=True):
        if file.endswith("ruleset.yaml"):
            continue
        logging.debug("loading file {}".format(file.title))
        rules = load_yaml(file)
        all_rules.extend(rules)
    return all_rules


def get_rule_features(paths: list[str], all=True) -> list[list[str]]:
    nested_rules = []
    simple_rules = []
    for path in paths:
        for rule in load_rules(path):
            row = [
                get_id(rule),
                get_message(rule),
                get_when(rule)
            ]
            if has_nested_condition(rule):
                nested_rules.append(row)
            else:
                simple_rules.append(row)
    if all:
        simple_rules.extend(nested_rules)
    return simple_rules


def when_to_simple_query(when: dict) -> str:
    if not when:
        return ""
    keys = list(when.keys())
    if len(keys) == 1:
        cond: str = keys[0]
        if cond.lower() in ["and", "or"]:
            child_queries = []
            for child in when[cond]:
                child_queries.append(when_to_simple_query(child))
            join_with = " AND " if cond == "and" else " OR "
            return "({})".format(join_with.join(child_queries))
        elif type(when[cond]) == dict:
            params: dict = when[cond]
            pattern: str = params.get("pattern", "")
            return pattern
    return ""


def get_few_shot_examples_from_rules(paths: list[str], pType: PromptType) -> list[dict]:
    examples = []
    if pType == PromptType.SearchQueryGen:
        for row in get_rule_features(paths):
            query = when_to_simple_query(row[2])
            if query != "":
                examples.append(
                    {
                        "input": row[1],
                        "output": query,
                    }
                )
    return examples


if __name__ == "__main__":
    print(get_few_shot_examples_from_rules([
        "/rulesets/default/generated/"
    ], PromptType.SearchQueryGen))
