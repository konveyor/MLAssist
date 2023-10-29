from prompts import PromptType
from yaml import safe_load


def _original_output(o: str) -> str: return o


def _parse_list_output(o: str) -> list[str]:
    """
    Parses LLM output that is a list of items in the YAML format
    """
    parsed_lines = []
    for line in o.split("\n"):
        if line.startswith("-"):
            parsed_lines.append(line)
        elif len(parsed_lines) > 0:
            parsed_lines[-1] = "\n".join([parsed_lines[-1], line])
    return parsed_lines


def get_few_shot_examples(pType: PromptType) -> list[dict]:
    return _load_prompt_data_from_yaml(pType, dType="examples")


def get_test_cases(pType: PromptType) -> list[dict]:
    return _load_prompt_data_from_yaml(pType, dType="test_cases")


def _load_prompt_data_from_yaml(pType: PromptType, dType: str) -> list[dict]:
    examples_file = {
        PromptType.WhenBlockGen: "./{}/when_block.yaml".format(dType),
        PromptType.SearchQueryGen: "./{}/search_query.yaml".format(dType),
        PromptType.ReleaseNoteItemGen: "./{}/release_note.yaml".format(dType),
    }[pType]

    with open(examples_file) as f:
        return safe_load(f)


def parse_prompt_output(pType: PromptType, output: str) -> str | list[str]:
    return {
        PromptType.ReleaseNoteItemGen: _parse_list_output,
        PromptType.SearchQueryGen: _original_output,
        PromptType.WhenBlockGen: _original_output,
    }[pType](output)
