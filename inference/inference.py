import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import json 

from inference.postprocess import extract_answer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# base_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# eval_tokenizer = AutoTokenizer.from_pretrained(
#     base_model,
#     add_bos_token=True,
#     trust_remote_code=True,
# )
# ft_model = PeftModel.from_pretrained(base_model, "/home/featurize/work/TinyLLaMA/src/outputs/tinyllama-finetune-2024-04-16-16-04/checkpoint-1500")

def inference(ft_model, eval_tokenizer, query):
    infer_prompt = f"""You are an expert at extracting useful information from user queries. I need you to extract meta information from the user's query.  The extraction reults contain 'year', 'month', 'day', 'file content', 'file type' information for file retriever to locate the file. The extracted information should exclusively contain key-value pairs. Additionally, please generate 5 synonyms for the extracted 'file content'. Below are 5 examples that meet these requirements:
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
### query: {query}
### information: """

    model_input = eval_tokenizer(infer_prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        prediction = eval_tokenizer.decode(ft_model.generate(**model_input, max_new_tokens=150)[0], skip_special_tokens=True)

    prediction = extract_answer(prediction)

    if len(prediction) == 0:
        prediction = " "
    else:
        prediction = prediction["information"]
    return prediction
        