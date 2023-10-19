# Rule Doctor

Rule Doctor is a tool to examine and improve analyzer YAML rules.

### Pre-requisites

It uses OpenAI's GPT-4 model to generate suggestions to improve rules. You must have API access to GPT-4 model to use it.

Copy the `.env.sample` file to `.env`:

```sh
cp .env.sample .env
```

Create an OpenAPI key and add it to `.env` file:

```sh
export OPENAPI_KEY=<your-key-here>
```

Source the `.env` file prior to using the tool:

```sh
source .env
```

### Usage

Rule Doctor helps improve YAML rule descriptions.

Prior to examining rules, generate metadata for the rules by running `prepare` command:

```sh
go run . prepare --input <path-to-yaml-rules>
```

Point `--input` to a directory containing YAML rules.

Now, run the `check` command to examine the rules and get improvement suggestions:

```sh
go run . check
```

This is an interactive program that will go through each rule and suggest new descriptions wherever needed. Press `Y` to accept any choice, hit `ENTER` to reject. Press `X` to exit gracefully at any point. 

On graceful exit, the program will write a diff file `diff.yaml` containing the suggested changes to rules.


