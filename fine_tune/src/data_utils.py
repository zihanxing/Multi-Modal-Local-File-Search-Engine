from pathlib import Path
import json
import datasets
from datasets import DatasetDict
import torch
from functools import partial
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM




def create_prompt_formats(sample):
    """
    Format various fields of the sample ('instruction','output')
    Then concatenate them using two newline characters 
    :param sample: Sample dictionnary
    """
    INTRO_BLURB = "Below is an instruction that describes a task. Write a response that appropriately completes the request."
    INSTRUCTION_KEY = "### Instruct: You are an expert at extracting meta information from the user's query.  The extraction reults contain 'date_year', 'date_month', 'date_day', 'date_sort', 'file_content', 'file_type', 'video_hour', 'video_minute' information for file retriever to locate the file. The extracted information should exclusively contain key-value pairs. Additionally, please generate 5 synonyms for the extracted 'file_content'."
    QUERY_KEY = "### Query: "
    INFORMATION_KEY = "### Information: "
    END_KEY = "### End"
    
    blurb = f"\n{INTRO_BLURB}"
    instruction = f"{INSTRUCTION_KEY}"
    query = f"{sample['input']}"
    response = f"{sample['output']}"
    end = f"{END_KEY}"
    parts = [part for part in [blurb, instruction, query, response, end] if part]
    formatted_prompt = "\n\n".join(parts)
    sample["text"] = formatted_prompt
    
    return sample


# SOURCE https://github.com/databrickslabs/dolly/blob/master/training/trainer.py
def get_max_length(model):
    conf = model.config
    max_length = None
    for length_setting in ["n_positions", "max_position_embeddings", "seq_length"]:
        max_length = getattr(model.config, length_setting, None)
        if max_length:
            print(f"Found max lenth: {max_length}")
            break
    if not max_length:
        max_length = 1024
        print(f"Using default max length: {max_length}")
    return max_length


def preprocess_batch(batch, tokenizer, max_length):
    """
    Tokenizing a batch
    """
    return tokenizer(
        batch["text"],
        max_length=max_length,
        truncation=True,
    )

# SOURCE https://github.com/databrickslabs/dolly/blob/master/training/trainer.py
def preprocess_dataset(tokenizer: AutoTokenizer, max_length: int,seed, dataset):
    """Format & tokenize it so it is ready for training
    :param tokenizer (AutoTokenizer): Model Tokenizer
    :param max_length (int): Maximum number of tokens to emit from tokenizer
    """
    
    # Add prompt to each sample
    print("Preprocessing dataset...")
    dataset = dataset.map(create_prompt_formats)#, batched=True)
    
    # Apply preprocessing to each batch of the dataset & and remove 'instruction', 'context', 'response', 'category' fields
    _preprocessing_function = partial(preprocess_batch, max_length=max_length, tokenizer=tokenizer)
    dataset = dataset.map(
        _preprocessing_function,
        batched=True,
        remove_columns=['input', 'output'],
    )

    # Filter out samples that have input_ids exceeding max_length
    dataset = dataset.filter(lambda sample: len(sample["input_ids"]) < max_length)
    
    # Shuffle dataset
    dataset = dataset.shuffle(seed=seed)

    return dataset



# model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# tokenizer = AutoTokenizer.from_pretrained(model_name,trust_remote_code=True,padding_side="left",add_eos_token=True,add_bos_token=True,use_fast=False)
# tokenizer.pad_token = tokenizer.eos_token

# model = AutoModelForCausalLM.from_pretrained(model_name)
# max_length = get_max_length(model)

def load_dataset(tokenizer, data_dir = "/home/featurize/work/TinyLLaMA/src/query_finetune.json"):

    seed = 666
    max_length = 2048
    
    with open(data_dir, "r") as f:
        query = json.load(f)
    query_data = [create_prompt_formats(row) for row in query] 
    query_dataset = datasets.Dataset.from_pandas(pd.DataFrame(data=query_data))
    data_split = query_dataset.train_test_split(test_size=0.2, seed=42)

    train_dataset =  data_split['train']
    val_dataset = data_split['test']

    train_dataset = preprocess_dataset(tokenizer, max_length,seed,train_dataset)
    eval_dataset = preprocess_dataset(tokenizer, max_length,seed, val_dataset)
    
    return train_dataset, eval_dataset
