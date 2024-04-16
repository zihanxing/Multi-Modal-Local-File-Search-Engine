from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from inference import inference
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

config = PeftConfig.from_pretrained("HongxuanLi/TinyLLaMA-RS")
model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = PeftModel.from_pretrained(model, "HongxuanLi/TinyLLaMA-RS").to(device)
tokenizer = AutoTokenizer.from_pretrained( "TinyLlama/TinyLlama-1.1B-Chat-v1.0", add_bos_token=True, trust_remote_code=True)


def get_llama_inference(query):
    result = inference.inference(model,tokenizer,query)
    return result