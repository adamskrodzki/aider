"""
Refinement message templates for the Coder class.
"""

preliminary_message_improvement_prompt = (
    "Your task is to improve (if possible) the following user's request:\n{inp}\n\n"
    "So it is more useful for an expert software developer to understand and carry out the user's request. "
    "Rewrite the request in a concise, factually correct manner, include relevant details from the context above. "
    "If possible, provide a detailed plan on how to carry out the task, but avoid writing code, as that will be done by the software developer in the next step. "
    "If the provided context contains relevant information, cite that information. "
    "If the provided context is empty or irrelevant to the user's request, do not make up any generic information, "
    "just improve the wording of the request."
)
