#!/usr/bin/env python3
import sys
import tiktoken

def count_tokens(model, file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} <file_path> <model>')
        print(f'Example: {sys.argv[0]} ./myprompt.txt "gpt-4"')
        sys.exit(1)
    
    file_path = sys.argv[1]
    model = sys.argv[2]
    # Get the token count
    token_count = count_tokens(model, file_path)
    print(f'The text file "{file_path}" contains {token_count} tokens as per "{model}".')