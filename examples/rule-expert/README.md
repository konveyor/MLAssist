# Rule Expert

Rule Expert is an experimental AI tool to work with Analyzer Rules.

## Skills

Rule Expert is a set of components with each component providing a specific skill to work with analyzer rules.
* Rule Generation Skill
  * Generate a minimal testable analyzer rule using natural language description about a removed or deprecated API.
* Rule Improvement Skill
  * Improve an existing analyzer rule.

## Usage 

> You need API access to OpenAI's `gpt-3.5-turbo` model to run the tool. Generate an API key.

Copy `.env.sample` file to `.env`:

```sh
cp .env.sample .env
```

Edit `.env` file and add your key:

```sh
export OPENAI_KEY="your-key-here"
```

Source `.env` file:

```sh
source .env
```

Setup virtualenv and install dependencies from `requirements.txt`.

### Rule Generation

This skill allows the tool to read a release note and generate analyzer rules for deprecated and removed APIs identified in the release note.

Several test release notes are available in `./test-cases/release_note.yaml` for quick testing.

To run the tool using one of the test-cases, simply execute the `main.py` file: 

```sh
python main.py
```

The result will be generated in `output_rules.yaml` file.

![Rule_Expert](https://github.com/konveyor-ecosystem/MLAssist/assets/9839757/29cf3cb9-ea27-4fc0-a33f-d45b259bc308)