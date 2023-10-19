package main

import (
	"bytes"
	"context"
	"fmt"
	"html/template"
	"log"
	"os"

	"github.com/sashabaranov/go-openai"
)

const updateDescriptionTemplate = `
I am using a source code analysis tool. It is a rule engine to analyse source code based on a set of input rules. 
A rule contains a search query, a message and a descritpion like: 

"""
- ruleID: test-rule
  searchQuery:
    javaclass.referenced:
      pattern: java.io.*
  message: "Found java.io.{{ className }}"
  description: | 
    Rule that searches for usage of packages in java.io
"""

When a rule matches, the file and line number where it matched in the source code is returned which is called an incident.
When a rule matches, the engine generates a response that looks like:

"""
- ruleID: <ruleID>
   description: <description>
   incidents:
   - incidentID: <id>
     message: <message>
     lineNumber: <number>
     fileURI: <fileURI>
     codeSnippet: <matchedCodeSnippet>
"""

The 'message' field in the rule can contain templated variables enclosed in '{' and '}'. 
For instance, in the example earlier, message field contains variable '{{className}}'. When the rule matches, the rule engine replaces '{{className}}' in 'message' with actual name of the Java class where rule matched and creates an incident. 
For the rule earlier, we can get matches like:

"""
- ruleID: test-rule
   description: |
    Rule that searches for usage of packages in java.io
   incidents:
   - incidentID: 1
     message: "Found java.io.File"
     lineNumber: 10
     file: file://src/main/java/File.java
     codeSnippet: |
      import java.io.File
   - incidentID: 1
     message: "Found java.io.FileWriter"
     lineNumber: 12
     file: file://src/main/java/FileWriter.java
     codeSnippet: |
      import java.io.FileWriter
"""


Since the rule engine will interpolate the values of templated variable '{{className}}' based on exact content of the match, the 'message' field for each incident is different. 
However, the 'description' field is not interpolated because it is applicable for a rule as a whole and is not specific to the match. 
I have a set of rules that I want to use with the tool. But these rules contain 'description' that have template variables too. 
Since the variables in the 'description' field are not interpolated by the rule engine, the responses contain those templates as-is and create a bad user experience for someone looking at the output. 

See following example:
"""
- description: |
    'org.apache.camel.impl.{SupportClass}' has been moved
  targets:
    - camel3+
    - camel
  sources:
    - camel2
    - camel
  message: The class 'org.apache.camel.impl.{{SupportClass}}' has been moved to 'org.apache.camel.support.{{SupportClass}}'. It has been moved out of 'org.apache.camel:camel-core' and into 'org.apache.camel:camel-support'.
  name: java-generic-information-00001
"""

For the above rule, the variable '{SupportClass}' is not interpolated. Note that there could be multiple template variables in description.
I want to update these descriptions and make them more generic such that they will be applicable to all incidents and don't contain the templated variables. 

The extra contextual information is already present in the 'message' field and other fields such as 'sources' and 'targets'. Based on that I updated the description to something like: 

"""
Classes under 'org.apache.camel.impl' are moved to 'org.apache.camel.support'
"""

Similarly, can you help me update description for the following rule? 

"""
<<<<.>>>>
"""

Only output the description in your response without any other characters (including quotes). If it's multi-line, put a newline after the first line.
`

func suggestNewDescription(ruleContent string, dryRun bool) (string, error) {
	openApiKey, ok := os.LookupEnv("OPENAPI_KEY")
	if !ok {
		return "", fmt.Errorf("OPENAPI_KEY not set")
	}
	client := openai.NewClient(openApiKey)
	var msg bytes.Buffer
	msgTemplate, err := template.New("msg").Delims("<<<<", ">>>>").Parse(updateDescriptionTemplate)
	if err != nil {
		return "", err
	}
	err = msgTemplate.Execute(&msg, ruleContent)
	if err != nil {
		return "", err
	}
	if !dryRun {
		resp, err := client.CreateChatCompletion(context.Background(), openai.ChatCompletionRequest{
			Model: openai.GPT4,
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleUser,
					Content: msg.String(),
				},
			},
		})
		if err != nil {
			return "", err
		}
		return resp.Choices[0].Message.Content, nil
	} else {
		log.Printf("dry run set, not creating prompt")
		return ruleContent, nil
	}
}
