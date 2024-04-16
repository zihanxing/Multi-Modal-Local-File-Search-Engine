import torch
import wandb, os
from train import finetune
import argparse
from pathlib import Path

def main():
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--max_steps", type=int, default=2000)
    parser.add_argument("--logging", type=int, default=50)
    parser.add_argument("--lr", type=float, default=1e-5)#2.5e-5
    parser.add_argument("--output_dir", type=str, default="./outputs")
    parser.add_argument("--data_root_dir", type=str, default="/home/featurize/work/TinyLLaMA/src/data")
    args = parser.parse_args()

    
    # create dataset
    data_dir = Path(args.data_root_dir) / "query_finetune.json"
    
    
    # model quantization

    
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    finetune(model_name, Path(data_dir), args)
    

    
if __name__ == "__main__":
    
    os.environ["WANDB_API_KEY"]= "2f548926b1a03960bd0e22b44bf54dbd530a7b50"
    # # login wandb
    # wandb.login()
    wandb_project = "tinyllama-finetune"
    if len(wandb_project) > 0:
        os.environ["WANDB_PROJECT"] = wandb_project
    main()
    
    
    