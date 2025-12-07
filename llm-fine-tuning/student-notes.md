# LLM Fine-Tuning: Student Notes

## 2-Day Technical Workshop

---

## Day 1: Foundations

### Why Fine-Tune an LLM?

**Key Reasons:**
1. **Domain Expertise** - Teach specialized knowledge in medicine, law, finance, or your industry
2. **Style & Tone** - Match your brand voice, communication style, or specific output formats
3. **Performance** - Smaller fine-tuned models can outperform larger general models on specific tasks

**Key Insight:** Fine-tuning teaches the model *how* to respond, while RAG provides *what* to respond with. They're complementary approaches.

---

### Fine-Tuning vs Alternatives

| Approach | Best For | Cost | Complexity |
|----------|----------|------|------------|
| Prompt Engineering | Quick iterations, general tasks | Low (API costs only) | Low |
| RAG | Knowledge-intensive, up-to-date info | Medium | Medium |
| Fine-Tuning | Style, format, specialized behavior | Medium-High | High |
| Pre-Training | Entirely new domains/languages | Very High | Very High |

**Rule of Thumb:** Start with prompting, add RAG for knowledge, fine-tune for behavior. Pre-train only if absolutely necessary.

---

### When to Fine-Tune

**Good Candidates:**
- Consistent output format required
- Specific writing style or tone
- Domain-specific terminology
- Reducing prompt length/cost
- Improving task-specific accuracy
- Teaching new behaviors

**Not Ideal For:**
- Frequently changing information
- Factual knowledge injection
- Tasks achievable with prompting
- Limited training data (<100 examples)
- Highly diverse task requirements
- Quick prototyping needs

---

### Types of Fine-Tuning

| Method | Parameters Trained | Key Characteristic |
|--------|-------------------|-------------------|
| Full Fine-Tuning | 100% | All parameters updated |
| LoRA | 0.1-1% | Low-rank adapter matrices |
| QLoRA | 0.1-1% | Quantized base + LoRA |
| Adapters | ~1% | Bottleneck layers |

---

### Full Fine-Tuning

**How It Works:** Update all model parameters during training on your dataset.

**Pros:**
- Maximum flexibility
- Best potential performance
- Full model customization

**Cons:**
- Requires massive GPU memory
- Risk of catastrophic forgetting
- Expensive and time-consuming

**Memory Requirements:**
| Model | Parameters | GPU RAM |
|-------|-----------|---------|
| Llama 2 7B | 7B | ~56 GB |
| Llama 2 13B | 13B | ~104 GB |
| Llama 2 70B | 70B | ~560 GB |

**Note:** Full fine-tuning requires ~8x model size in GPU memory (model + gradients + optimizer states)

---

### LoRA: Low-Rank Adaptation

**The Key Insight:** Weight updates during fine-tuning have low intrinsic rank. Instead of updating the full weight matrix, we add small trainable matrices.

```python
from peft import LoraConfig

config = LoraConfig(
    r=16,              # Rank
    lora_alpha=32,     # Scaling
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
)
```

**LoRA Benefits:**
- 90-99% fewer trainable parameters
- Fits on consumer GPUs
- No inference latency added
- Easy to swap/combine adapters
- Preserves base model knowledge

**Key Metrics:**
- ~1% trainable parameters
- 10-50x memory savings

---

### QLoRA: Quantized LoRA

**Fine-tune 65B models on a single 48GB GPU**

**Three Key Innovations:**
1. **4-bit Quantization** - Base model stored in 4-bit NormalFloat format, reducing memory by 4x
2. **Double Quantization** - Quantize the quantization constants for additional memory savings
3. **Paged Optimizers** - Handle memory spikes by offloading to CPU when needed

```python
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
```

---

### Memory Requirements Comparison

| Model | Full FT | LoRA (16-bit) | QLoRA (4-bit) |
|-------|---------|---------------|---------------|
| Llama 2 7B | ~56 GB | ~16 GB | ~6 GB |
| Llama 2 13B | ~104 GB | ~32 GB | ~10 GB |
| Llama 2 70B | ~560 GB | ~160 GB | ~48 GB |
| Mistral 7B | ~56 GB | ~16 GB | ~6 GB |

**Practical Impact:** QLoRA enables fine-tuning a 7B model on a single RTX 3090/4090 (24GB) or even RTX 3080 (10GB) for smaller models!

---

### Data Preparation

**Data Quality Matters Most:**
- Quality over quantity - 1000 good examples beat 10000 noisy ones
- Diverse examples covering edge cases
- Consistent formatting and structure
- Representative of production use

**Dataset Sizes:**
| Scale | Examples |
|-------|----------|
| Minimum | 100+ |
| Typical | 1-10K |
| Large Scale | 50K+ |

**Data Sources:**
- Existing labeled datasets
- Production logs (with consent)
- Expert annotations
- Synthetic data from stronger models
- Human preference comparisons

**Caution:** Ensure data licensing allows training. Check for PII and sensitive content.

---

### Training Data Formats

**Instruction Format:**
```json
{
  "instruction": "Summarize the text",
  "input": "Long article text...",
  "output": "Brief summary..."
}
```

**Chat Format:**
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

**Completion Format:**
```json
{
  "prompt": "### Question:\nWhat is...\n\n### Answer:\n",
  "completion": "The answer is..."
}
```

**Best Practice:** Use the same prompt template during training and inference for consistent results.

---

### The Hugging Face Ecosystem

| Library | Purpose |
|---------|---------|
| **Transformers** | Model loading, tokenization, inference |
| **Datasets** | Efficient data loading and processing |
| **PEFT** | LoRA, adapters, prompt tuning |
| **TRL** | SFT, RLHF, DPO training |

```python
# Essential imports for fine-tuning
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import get_peft_model, LoraConfig
from trl import SFTTrainer
from datasets import load_dataset
```

---

### Training Infrastructure Options

| Platform | GPUs | Cost | Best For |
|----------|------|------|----------|
| Local GPU | RTX 3090/4090 | Upfront cost | Experimentation, small models |
| Google Colab Pro | T4, A100 | $10-50/mo | Learning, prototyping |
| RunPod / Vast.ai | Various | $0.20-2/hr | Flexible, cost-effective |
| AWS / GCP / Azure | A100, H100 | $2-30/hr | Production, enterprise |
| Lambda Labs | A100, H100 | $1-2/hr | ML-focused, great value |

---

## Day 2: Hands-On Fine-Tuning

### The Fine-Tuning Pipeline

1. **Prepare Data** → 2. **Load Model** → 3. **Configure LoRA** → 4. **Train** → 5. **Evaluate** → 6. **Deploy**

**Data Preparation:**
- Format conversion
- Train/eval split
- Tokenization

**Training:**
- Hyperparameter tuning
- Monitoring loss
- Checkpointing

**Deployment:**
- Merge adapters
- Quantize for inference
- Serve at scale

---

### Complete Fine-Tuning Example

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig

# 1. Load quantized model
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    quantization_config=bnb_config
)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

# 2. Configure LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
)
model = get_peft_model(model, lora_config)

# 3. Train
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=SFTConfig(output_dir="./output", num_train_epochs=3)
)
trainer.train()
```

---

### Key Hyperparameters

**LoRA Parameters:**
| Parameter | Typical Values | Effect |
|-----------|---------------|--------|
| `r` (rank) | 8, 16, 32, 64 | Capacity of adaptation |
| `lora_alpha` | 16, 32, 64 | Scaling factor |
| `lora_dropout` | 0.0, 0.05, 0.1 | Regularization |
| `target_modules` | q,k,v,o proj | Which layers to adapt |

**Training Parameters:**
| Parameter | Typical Values |
|-----------|---------------|
| Learning rate | 1e-4 to 3e-4 |
| Batch size | 4-32 (with gradient accum) |
| Epochs | 1-5 |
| Warmup ratio | 0.03-0.1 |
| Weight decay | 0.0-0.01 |

**Start Conservative:** r=16, lora_alpha=32, lr=2e-4, 3 epochs. Tune from there based on results.

---

### Evaluation Metrics

**Training Metrics:**
- **Loss:** Should decrease
- **Perplexity:** Lower is better
- **Gradient norm:** Stability indicator

**Task Metrics:**
- **Accuracy:** Classification
- **ROUGE/BLEU:** Generation
- **F1 Score:** Extraction

**Human Eval:**
- **A/B testing:** Preference
- **Rating scales:** Quality
- **Error analysis:** Failure modes

**Critical:** Always evaluate on a held-out test set that wasn't used during training. Watch for overfitting!

---

### Common Issues & Solutions

| Issue | Signs | Solutions |
|-------|-------|-----------|
| **Overfitting** | Training loss drops, eval loss increases | More data, fewer epochs, higher dropout, lower r |
| **Catastrophic Forgetting** | Model loses general capabilities | Lower learning rate, use LoRA, include diverse data |
| **Unstable Training** | Loss spikes, NaN values | Lower learning rate, gradient clipping, check data |
| **Poor Generation Quality** | Repetitive, nonsensical output | Check data quality, adjust sampling params |

---

### Merging & Deployment

**Merge LoRA Weights:**
```python
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
model = PeftModel.from_pretrained(base_model, "./lora-adapter")

# Merge and save
merged = model.merge_and_unload()
merged.save_pretrained("./merged-model")
```

**Deployment Options:**
| Tool | Use Case |
|------|----------|
| **vLLM** | High-throughput serving |
| **TGI** | Hugging Face inference |
| **Ollama** | Local deployment |
| **LMDeploy** | Efficient inference |
| **llama.cpp** | CPU inference |

**Pro Tip:** Keep adapters separate for easy A/B testing and rollback capabilities.

---

### Quantization for Inference

| Format | Bits | Quality Loss | Speed | Use Case |
|--------|------|-------------|-------|----------|
| FP16/BF16 | 16 | None | 1x | Default inference |
| INT8 | 8 | Minimal | 1.5-2x | Production serving |
| GPTQ/AWQ | 4 | Small | 2-3x | Memory-constrained |
| GGUF (Q4) | 4 | Small | Varies | CPU / Local |

**Export to GGUF for Ollama:**
```bash
python llama.cpp/convert.py ./merged-model --outtype f16
./llama.cpp/quantize ./model.gguf ./model-q4.gguf q4_k_m
```

---

### Cost Optimization Strategies

**Training Costs:**
- Use spot/preemptible instances
- Start with smaller models
- Use gradient accumulation
- Early stopping

**Storage Costs:**
- Store only adapters (MBs vs GBs)
- Quantize final models
- Use model hubs
- Clean up checkpoints

**Inference Costs:**
- Quantize models
- Batch requests
- Use efficient serving
- Cache common queries

**Estimated Training Costs:**
| Model | QLoRA Training Cost |
|-------|---------------------|
| 7B Model | $5-50 |
| 13B Model | $50-200 |
| 70B Model | $200-1000 |
| Cost Reduction vs Full FT | 10-100x |

---

### Production Best Practices

**Do:**
- Version control your data and configs
- Log all experiments with W&B/MLflow
- Start with proven base models
- Evaluate on multiple metrics
- Test in staging before production
- Monitor model performance over time
- Keep rollback capability

**Don't:**
- Skip data validation
- Train on test data
- Ignore evaluation metrics
- Deploy without testing
- Forget about edge cases
- Use unlicensed data
- Ignore safety evaluations

---

### Beyond SFT: RLHF & DPO

**RLHF (Reinforcement Learning from Human Feedback):**
- Train a reward model from human preferences, then use PPO to optimize the LLM
- More complex to implement
- Requires reward model training
- Can achieve strong alignment

**DPO (Direct Preference Optimization):**
- Directly optimize on preference pairs without a separate reward model
- Simpler than RLHF
- No reward model needed
- Stable training

```python
from trl import DPOTrainer, DPOConfig

# DPO requires preference pairs: (prompt, chosen, rejected)
trainer = DPOTrainer(model=model, ref_model=ref_model, train_dataset=preference_dataset)
```

---

### Safety Considerations

**Risks:**
- Harmful content generation
- Bias amplification
- Privacy leaks from training data
- Jailbreak vulnerabilities

**Mitigations:**
- Red-team testing
- Safety-focused training data
- Output filtering
- Monitoring & logging

**Evaluation Benchmarks:**
- ToxiGen benchmark
- TruthfulQA
- BBQ (bias)
- Custom safety tests

**Important:** Fine-tuning can remove safety guardrails present in the base model. Always test for safety regressions.

---

### Tools & Resources

**Libraries:**
- Hugging Face PEFT
- TRL
- Unsloth
- Axolotl

**Platforms:**
- Hugging Face Hub
- RunPod
- Lambda Labs
- Modal

**Tracking:**
- Weights & Biases
- MLflow
- TensorBoard
- Neptune

**Serving:**
- vLLM
- TGI
- Ollama
- LiteLLM

---

### Key Takeaways

1. **When:** Fine-tune for behavior, style, format - not factual knowledge
2. **How:** LoRA/QLoRA makes it accessible on consumer hardware
3. **Deploy:** Merge, quantize, serve with vLLM/TGI/Ollama

**Final Note:** Fine-tuning has become accessible to everyone. Start small, iterate quickly, and always evaluate thoroughly before deployment.

---

## Contact

- Website: ai-elevate.ai
- Email: training@ai-elevate.ai
