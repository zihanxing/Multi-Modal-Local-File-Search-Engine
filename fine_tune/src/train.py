import torch
import transformers
from datetime import datetime
from data_utils import load_dataset
from pathlib import Path
from accelerate import FullyShardedDataParallelPlugin, Accelerator
from torch.distributed.fsdp.fully_sharded_data_parallel import FullOptimStateDictConfig, FullStateDictConfig
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import prepare_model_for_kbit_training
from peft import LoraConfig, get_peft_model

def finetune(model_name, data_dir, args):
    

        
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    # load model and tokenizer 
    tokenizer = AutoTokenizer.from_pretrained(model_name,
                                              add_eos_token=True,
                                              add_bos_token=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = '[PAD]'
    model = AutoModelForCausalLM.from_pretrained(model_name, 
                                                 quantization_config=bnb_config, 
                                                 device_map={'':torch.cuda.current_device()})
    

    # load tokenized dataset
    train_dataset, val_dataset = load_dataset(tokenizer,  data_dir)
    
    
    # set accelerator 
    fsdp_plugin = FullyShardedDataParallelPlugin(
        state_dict_config=FullStateDictConfig(offload_to_cpu=True, rank0_only=False),
        optim_state_dict_config=FullOptimStateDictConfig(offload_to_cpu=True, rank0_only=False),
    )
    accelerator = Accelerator(fsdp_plugin=fsdp_plugin)   
    
    # use lora
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)
    # config = LoraConfig(
    #     r=16,
    #     lora_alpha=32,
    #     lora_dropout=0.05,
    #     bias="none",
    #     task_type="CAUSAL_LM"
    # )
    config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
            "lm_head",
        ],
        bias="none",
        lora_dropout=0.05,  # Conventional
        task_type="CAUSAL_LM",
    )
    
    model.enable_input_require_grads()
    model = get_peft_model(model, config)


    # apply the accelerator. 
    model = accelerator.prepare_model(model)
    
    if torch.cuda.device_count() > 1: # If more than 1 GPU
        model.is_parallelizable = True
        model.model_parallel = True
    
    
    project = "tinyllama-finetune"
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # model = model.to(device)

    trainer = transformers.Trainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        args=transformers.TrainingArguments(
            output_dir=Path(args.output_dir) / f"{project}-{datetime.now().strftime('%Y-%m-%d-%H-%M')}",
            warmup_steps=5,
            per_device_train_batch_size=4,
            gradient_checkpointing=True,
            gradient_accumulation_steps=4,
            max_steps=args.max_steps,
            learning_rate=args.lr,
            logging_steps=args.logging,
            bf16=True,
            optim="paged_adamw_8bit",
            logging_dir=Path(args.output_dir) / "logs",        # Directory for storing logs
            save_strategy="steps",       
            save_steps=25,               # Save checkpoints every 50 steps
            evaluation_strategy="steps", # Evaluate the model every logging step
            eval_steps=50,               # Evaluate and save checkpoints every 50 steps
            do_eval=True,                # Perform evaluation at the end of training
            report_to="wandb",           
            run_name=f"{project}-{datetime.now().strftime('%Y-%m-%d-%H-%M')}"          # Name of the W&B run (optional)
        ),
        data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    model.config.use_cache = False
    trainer.train()
