# Refine Code Instructions

## ME

````
Please refine the following instruction for ChatGPT: """
Please modify the above Python program code to work correctly as specified in the description.
Please observe the following rules when outputting code.

- Code is enclosed in Markdown code blocks.
- Formatted to be executable with Python's exec function.
- Keep the modified code as many characters as possible as the original code.
- Do not add or delete comment text.
- Do not add or delete whitespace or.
- Do not add or delete line break characters.
- Do not change variable or function names.
- Please modify the code to be closer to the unmodified code than the following model solution.

# Problem Description
{description}

# Incorrect code
```python
{incorrect_code}
```

# Model solution
```python
{correct_code}
```
"""
````

## ChatGPT

Certainly! Here's a refined version of your instruction:

### Instruction for ChatGPT:

Please amend the provided Python program code to align with the described functionality. When suggesting code changes, adhere to these guidelines:

1. Enclose the code within Markdown code blocks.
2. Ensure it's executable using Python's exec function.
3. Retain as much of the original code's character count as possible.
4. Maintain existing comments unchanged.
5. Preserve whitespace and indentation.
6. Maintain the original line breaks.
7. Keep variable and function names intact.
8. Ensure the amended code remains closer in structure to the original, rather than resembling the model solution provided.

### Problem Description:

{description}

Incorrect Code:

```python
{incorrect_code}
```

### Model Solution (for reference):

```python
{correct_code}
```

This instruction clearly communicates the task at hand, with a concise and organized structure.
