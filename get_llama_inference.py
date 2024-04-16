from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from inference import inference
import torch

# Check if GPU is available and choose the device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the configuration for the PEFT model
config = PeftConfig.from_pretrained("HongxuanLi/TinyLLaMA-RS")

# Load the pre-trained model for chat generation
model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Wrap the pre-trained model with PEFT for fine-tuning
model = PeftModel.from_pretrained(model, "HongxuanLi/TinyLLaMA-RS").to(device)

# Load the tokenizer for the pre-trained model
tokenizer = AutoTokenizer.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    add_bos_token=True,  # Add beginning of sequence token
    trust_remote_code=True  # Trust remote code (if necessary)
)

def get_llama_inference(query):
    """
    Get inference from the TinyLLaMA model.

    Args:
        query (str): Input text query.

    Returns:
        str: Generated response from the model.
    """
    result = inference.inference(model, tokenizer, query)
    return result
