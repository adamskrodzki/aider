"""
Refinement message templates for the Coder class.
"""

preliminary_message_improvement_prompt = """
 Here is a prompt provided by very lazy user:
 PROMPT
 {prompt}

END OF PROMPT

 Your task is to refine this prompt in line with instructions in your system message. Refined prompt will be targeted to Software Developer. 
 Make sure that refined prompt allows this Software Developer to carry on the task in most effective way.
Help by improving prompt's quality by:
    - improvment of clarity of the prompt
    - removal of meaningless or misliding statements
    - emphasis on important information
    - adding references to relevaant code included after  'Here is the current content of the files' 
    - taking into account relevant information from history of conversation
    - providing step by step guidance on how to carry on the task in best possible way.

    Keep prompt maximally concise, but remember to not remove any relevant information
 Refined Prompt:
"""
system_message = """
    Act as expert prompt engineer. Your task is to refine user's prompt to enable less capable Large Language Model (acting as software developer)
    To answer this refined prompt in best possible way. Help by improving prompt's quality by:
    - improvment of clarity of the prompt
    - removal of meaningless or misliding statements
    - emphasis on important information
    - adding references to relevaant code included in  *read-write* files
    - taking into account relevant information from history of conversation
    - providing step by step guidance on how to carry on the task in best possible way.

    Keep prompt maximally concise, but remember to not remove any relevant information
    """
