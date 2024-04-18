import re
from pprint import pprint
import ast

def preprocess(input_str):

    # Escaping single quotes inside the string
    escaped_str = input_str.replace("'", "\\'")
    
    # Wrapping the escaped string in additional quotes for evaluation
    eval_str = f"'{escaped_str}'"
    
    try:
        # Attempt to evaluate the preprocessed string
        return ast.literal_eval(eval_str)
    except SyntaxError as e:
        print(f"Error evaluating string: {e}")
        print(eval_str)
        return " "

def extract_answer(prediction):

    # Extracting the part of the text after the specified prompt
    relevant_part = prediction.split("Now, please extract meta information from this user query:")[-1].strip()

    # Updated regex pattern to accommodate potential variations in formatting
    pattern = r"### query:\s*(.*?)\n### information:\s*(\{.*?\})\s*"

    # Search for the pattern in the relevant part of the text
    match = re.search(pattern, relevant_part, re.DOTALL)

    extracted_information = {}

    if match:
        # Extract query and information string
        query, information_str = match.groups()
        # Convert information string into a Python dictionary
        information = preprocess(information_str)
        extracted_information["query"] = query
        extracted_information["information"] = information
    return extracted_information