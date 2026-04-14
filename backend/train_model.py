"""
Medical AI Model Fine-Tuning Script
=====================================
Fine-tunes TinyLlama-1.1B-Chat on medical Q&A data using LoRA/PEFT.

Usage:
    cd backend
    python train_model.py

Requirements (add via: pip install transformers datasets peft trl torch accelerate):
    transformers>=4.40.0, datasets>=2.18.0, peft>=0.10.0,
    trl>=0.8.0, torch>=2.2.0, accelerate>=0.27.0

Output:
    LoRA adapter saved to: backend/models/medical_lora_adapter/
    After training, set LOCAL_AI_ADAPTER_PATH=models/medical_lora_adapter in .env
"""

import json
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "medical_finetune_dataset.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "models", "medical_lora_adapter")

LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "v_proj"]

NUM_TRAIN_EPOCHS = 3
PER_DEVICE_BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 4
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 512
WARMUP_STEPS = 10
LOGGING_STEPS = 5

# ---------------------------------------------------------------------------
# Prompt template (TinyLlama special tokens kept as strings)
# ---------------------------------------------------------------------------
SYS_TOK  = "<" + "|system|>"
USER_TOK = "<" + "|user|>"
ASST_TOK = "<" + "|assistant|>"
EOS_TOK  = "</s>"

SYSTEM_MSG = (
    "You are HealthBot, a compassionate AI healthcare assistant. "
    "You provide accurate, helpful health information with empathy. "
    "You never diagnose conditions or prescribe medications. "
    "Always remind users to consult healthcare professionals for personalised advice."
)


def format_prompt(example: dict) -> dict:
    """Format a dataset entry into the TinyLlama chat template string."""
    text = (
        SYS_TOK + "\n" + SYSTEM_MSG + EOS_TOK + "\n"
        + USER_TOK + "\n" + example["input"].strip() + EOS_TOK + "\n"
        + ASST_TOK + "\n" + example["output"].strip() + EOS_TOK
    )
    return {"text": text}


# ---------------------------------------------------------------------------
# Main training pipeline
# ---------------------------------------------------------------------------
def main():
    try:
        import torch
        from datasets import Dataset
        from transformers import (
            AutoTokenizer,
            AutoModelForCausalLM,
            TrainingArguments,
            BitsAndBytesConfig,
        )
        from peft import LoraConfig, get_peft_model, TaskType
        from trl import SFTTrainer, SFTConfig
    except ImportError as e:
        logger.error(
            f"Missing dependency: {e}\n"
            "Run: pip install transformers datasets peft trl torch accelerate"
        )
        raise SystemExit(1)

    # ── Dataset ──────────────────────────────────────────────────────────────
    logger.info("Loading dataset...")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    logger.info(f"  {len(raw_data)} examples found")

    dataset = Dataset.from_list(raw_data)
    dataset = dataset.map(format_prompt, remove_columns=dataset.column_names)
    logger.info("  Dataset formatted successfully")

    # ── Tokenizer ─────────────────────────────────────────────────────────────
    logger.info(f"Loading tokenizer: {BASE_MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # ── Model ─────────────────────────────────────────────────────────────────
    use_gpu = torch.cuda.is_available()
    logger.info(f"{'GPU (CUDA)' if use_gpu else 'CPU'} training mode detected")

    load_kwargs = {
        "trust_remote_code": True,
        "torch_dtype": torch.float16 if use_gpu else torch.float32,
    }
    if use_gpu:
        load_kwargs["device_map"] = "auto"

    logger.info(f"Loading base model: {BASE_MODEL_ID} ...")
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_ID, **load_kwargs)
    model.config.use_cache = False
    model.config.pretraining_tp = 1

    # ── LoRA Config ───────────────────────────────────────────────────────────
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ── Training Arguments ────────────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_TRAIN_EPOCHS,
        per_device_train_batch_size=PER_DEVICE_BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        warmup_steps=WARMUP_STEPS,
        logging_steps=LOGGING_STEPS,
        save_strategy="epoch",
        fp16=use_gpu,
        bf16=False,
        optim="adamw_torch",
        report_to="none",
        max_seq_length=MAX_SEQ_LENGTH,
        dataset_text_field="text",
    )

    # ── Trainer ───────────────────────────────────────────────────────────────
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    logger.info("Starting fine-tuning...")
    trainer.train()

    # ── Save adapter ──────────────────────────────────────────────────────────
    logger.info(f"Saving LoRA adapter to: {OUTPUT_DIR}")
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    logger.info("Training complete!")
    logger.info(
        f"\nNext step:\n"
        f"  Add this to your .env file:\n"
        f"  LOCAL_AI_ADAPTER_PATH=models/medical_lora_adapter\n"
        f"  Then restart the backend server."
    )


if __name__ == "__main__":
    main()
