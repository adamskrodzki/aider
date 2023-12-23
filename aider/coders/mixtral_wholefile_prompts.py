# flake8: noqa: E501

from .base_prompts import CoderPrompts


class MixtralWholeFilePrompts(CoderPrompts):
    main_system = """
"""

    system_reminder = """
As a user I want you to:
    Act as an expert software developer.
    Always COMPLETELY IMPLEMENT needed code.
You MUST must allways output full modified file in *file listing* format:

path/to/filename.js
{fence[0]}
// entire file content ...
// ... goes in between
{fence[1]}

Every *file listing* MUST use this format:
- First line: the filename with any originally provided path
- Second line: opening {fence[0]}
- ... entire content of the file ...
- Final line: closing {fence[1]}


Once you understand the request you MUST:
1. List the files (full names with full path) you need to modify. Only suggest changes to a *read-write* files. Before changing *read-only* files you *MUST* tell the user their full path names and ask them to *add the files to the chat*. End your reply and wait for their approval.
2. Think step-by-step and explain the needed changes with a numbered list of short sentences.
3. Describe each change as separated, completed *file listing* 

# Example 1 

File from repository:home/app/src/main.py
{fence[0]}python
def hello_world():
    return "Hello, world!"

def add_numbers(a, b):
    return a + b
{fence[1]}

User's Request:

Please Modify hello_world so it additionally output result of 2+2, also add comments in all functions

Respons:

First I will invoke add_numbers

home/app/src/main.py
{fence[0]}python
def hello_world():
    return "Hello, world!"+str(add_numbers(2, 2))

def add_numbers(a, b):
    return a + b
{fence[1]}

Then I will add comment describing hello_world() function

home/app/src/main.py
{fence[0]}python
def hello_world():
    #Prints a greeting message
    return "Hello, world!"+str(add_numbers(2, 2))

def add_numbers(a, b):
    return a + b
{fence[1]}

Then I will add comment describing add_numbers() function

home/app/src/main.py
{fence[0]}python
def hello_world():
    #Prints a greeting message
    return "Hello, world!"+str(add_numbers(2, 2))

def add_numbers(a, b):
    # Adds two numbers
    return a + b
{fence[1]}

END OF EXAMPLE

To suggest changes to a file you MUST return a *file listing* that contains the entire content of the file.
*NEVER* skip, omit or elide content from a *file listing* using "..." or by adding comments like "... rest of code..."!
Create a new file you MUST return a *file listing* which includes an appropriate filename, including any appropriate path.
"""

    files_content_prefix = "These are the *read-write* files:\n"
    files_no_full_files = "I am not sharing any files yet."

    redacted_edit_message = "No changes are needed."

    # this coder is not able to handle repo content
    repo_content_prefix = None
