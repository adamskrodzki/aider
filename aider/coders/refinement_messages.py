"""
Refinement message templates for the Coder class.
"""

preliminary_message_improvement_prompt = """
# Create a Detailed, Structured Prompt for Coding Problem Development

## 1. Understand the Problem Context
- Carefully read the given problem statement or task description.
- Identify the core functionality that needs to be implemented or the primary problem that needs to be solved.

## 2. Define Specific Requirements
- Break down the overall task into smaller, manageable components.
- Clearly outline what each component of the code should achieve.
- Specify any constraints or special conditions that need to be considered (e.g., input ranges, data types).

## 3. Outline the Implementation Steps
- Provide a step-by-step approach to implement the solution.
- Each step should focus on a specific part of the problem, progressing logically from input validation to the final output.

## 4. Detail Error Handling and Edge Cases
- Highlight how the code should handle possible errors or exceptions including specific error messages.
- Mention edge cases and describe how the code should address them.

## 5. Focus on Clarity and Precision
- Use clear and precise language.
- Avoid ambiguity in instructions to ensure the generated code meets the requirements.
- Stay Concise

# EXAMPLE
Below for reference, example of good priming prompt for different problem:


Based on the provided instructions, the task is to modify the `find_anagrams` function in the `anagram.py` file to implement the logic for finding anagrams of a target word from a list of candidate words. Here's a detailed specification of the actions that need to be taken:
1. **Input Validation**:
   - Ensure that the input parameters `word` and `candidates` are of the correct type and format as per the instructions.
   - Check that the `word` is a non-empty string containing only ASCII alphabetic characters.
   - Verify that `candidates` is a list of non-empty strings containing only ASCII alphabetic characters.

2. **Anagram Detection**:
   - Iterate through each candidate word in the `candidates` list.
   - For each candidate word, check if it is an anagram of the `word` by comparing the sorted characters of both words.
   - If the sorted characters of the candidate word match the sorted characters of the target word (ignoring case), then the candidate word is an anagram of the target word.

3. **Case Sensitivity**:
   - Ensure that the case of the candidate words in the anagram set matches the case of the words in the original `candidates` list.

4. **Return Anagram Set**:
   - Create a list to store the anagrams of the target word.
   - Add the candidate words that are anagrams of the target word to the anagram set list.

5. **Return Result**:
   - Return the anagram set list as the result of the `find_anagrams` function.
"""
wrapped_message = (
    "Please review preliminary analysis which you might find useful: \n\n {analysis}\n"
)
