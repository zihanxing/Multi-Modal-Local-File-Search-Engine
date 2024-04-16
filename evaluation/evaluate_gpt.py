import re
from pprint import pprint
import ast
import google.generativeai as genai

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
        information = ast.literal_eval(information_str)
        extracted_information["query"] = query
        extracted_information["information"] = information
    return extracted_information

def evaluate_by_llm(truth, pred, model):
    pred = str(extract_answer(pred)["information"])
    truth = str(truth["output"])
    
    prompt = f"""
    You are an expert at evaluating LLMs predictions. The output contains 'year', 'month', 'day', 'file content', 'file type' information.
    'year', 'month', 'day' should be exactly the same. For 'file content' and 'file type', you can just qualitatively evaluate it by measuring the
    semantic similarty without being too strict. Based on the above evaluation metric, if you think the prediction is good, return 1, otherwise, return 0.
    your response should be only one numer: 0 or 1. Here is the ground truth label and prediction results.
    
    ### Ground Truth: {truth}
    ### Prediction: {pred}
        """
    if model == "gpt":
        client = OpenAI()
        response = client.chat.completions.create(
            model='gpt-4', #gpt-4
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt},
                    ],
                }
            ],
            max_tokens=2000,
        )
        eval_res = response.choices[0].message.content
     
    elif model == "gemini":
        GOOGLE_API_KEY = "AIzaSyBij2lnM23T5vH9BK1FwDVe01_j1RwDtF0"
        genai.configure(api_key=GOOGLE_API_KEY)

        # Using Gemini API
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        eval_res = response.candidates[0].content.parts[0].text
    return eval_res


def evaluate(model, tokenizer, testset_dir = "/home/featurize/work/TinyLLaMA/src/data/query_test.json"):

    with open(testset_dir, "r") as f:
        test_query = json.load(f)
    
    for query in test_query:
        eval_prompt = f""" You are an expert at extracting useful information from user queries. I need you to extract meta information from the user's query.  The extraction reults contain 'year', 'month', 'day', 'file content', 'file type' information for file retriever to locate the file. The extracted information should exclusively contain key-value pairs. Additionally, please generate 5 synonyms for the extracted 'file content'. Below are 5 examples that meet these requirements:
        Example1
        ### query: Project documentation from January 15, 2024, to February 20, 2024
        ### information: {{'year': [2024, 2024], 'month': [1, 2], 'day': [15, 20], 'file content': ['Project Documentation', 'Project Files', 'Project Overview', 'Project Details', 'Project Progress Documentation'], 'file type': ['pdf', 'doc', 'docx']}}

        Example2
        ### query: Find my photos from New York last summer
        ### information: {{'year': [-1, -1], 'month': [6, 8], 'day': [0, 0], 'file content': ['Photo taken in New York', 'New York Image', 'New York Snapshot', 'New York Picture', 'New York Photograph'], 'file type': ['jpg', 'jpeg', 'png', 'heif', 'tiff']}}

        Example3
        ### query: How is AI transforming healthcare diagnostics?
        ### information: {{'year': [], 'month': [], 'day': [], 'file content': ['AI in Healthcare Diagnostics', 'Artificial Intelligence and Medical Imaging', 'Machine Learning for Early Detection', 'AI Applications in Healthcare', 'Innovations in AI-based Diagnostics'], 'file type': ['pdf', 'docx', 'pptx', 'mp4', 'mp3']}}

        Example4
        ### query: Conference materials from the Global Tech Summit held from 2023/10/10 to 2023/10/12
        ### information: {{'year': [2023, 2023], 'month': [10, 10], 'day': [10, 12], 'file content' : ['Global Tech Summit Materials', 'Tech Summit Presentations', 'Tech Conference Docs', 'Tech Summit Slides', 'Tech Summit Proceedings'], 'file type': ['pdf', 'pptx', 'doc', 'docx']}}

        Example5
        ### query: The best ways to introduce coding to children
        ### information: {{'year': [], 'month': [], 'day': [], 'file content': ['Coding for Kids', 'Children\'s Programming Basics', 'Fun Coding Projects for Kids', 'Learning to Code Through Games', 'Introduction to Programming for Young Learners'], 'file type': ['pdf', 'docx', 'pptx', 'mp4']}}
        
        Example6
        ### query: The latest annual reports of ABC Ltd
        ### information: {{'year': [0, 0], 'month': [0, 0], 'day': [0, 0], 'file content': ['ABC Ltd. Annual Report', 'Yearly Financial Statement of ABC Ltd.', 'Annual Summary of ABC Ltd.', 'ABC Ltd. Year-End Report', 'ABC Ltd. Fiscal Year Report'], 'file type': ['pdf', 'xlsx', 'xls', 'docx', 'doc']}}

        Now, please extract meta information from this user query:
        ### query: {query['input']}
        ### information: """    


        model_input = tokenizer(eval_prompt, return_tensors="pt").to("cuda")
        ft_model.eval()
        
        acc = 0
        with torch.no_grad():
            prediction = eval_tokenizer.decode(ft_model.generate(**model_input, max_new_tokens=200)[0], skip_special_tokens=True)
        eval_res = evaluate_by_llm(truth, pred, model = 'gemini')
        try:
            acc += int(eval_res)
        except:
            if ("1" in eval_res and "0" not in eval_res):
                acc += 1
            else:
                acc += 0
    return acc / len(test_query)