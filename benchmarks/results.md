# Benchmark Results

All my test data from running LLMs on the Nova. Kept everything here so I don't forget what I tried.

---

## Test Environment

**Date:** January 7-8, 2026  
**Hardware:** Indiedroid Nova 16GB  
**OS:** Debian 12 (bookworm) aarch64  
**Kernel:** 6.1.0-1023-rockchip  
**RKLLM Runtime:** 1.2.1  
**NPU Driver:** v0.9.7  

---

## Llama 3.1 8B Instruct

**Model:** c01zaut/Llama-3.1-8B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-1.0  
**File Size:** 8.59 GB  
**Prompt:** "List all 50 US state capitals in alphabetical order by state name."

### What I got
- 3.72 tokens/second
- 411 tokens out
- Took about 110 seconds total
- Model loaded in ~17 seconds (RAM jumped from 790 MiB to 8.5 GiB)

### Resource Usage (while generating)
- **RAM:** Sat at 8.5-8.6 GiB the whole time. Model itself is about 7.7 GiB.
- **NPU:** Averaging 79% per core, peaked at 83%. All 3 cores stayed balanced.
- **CPU:** Basically idle (0-5%). NPU was doing the work.

### vs Pi 5
Jeff Geerling got 1.99 tok/s on Pi 5 16GB with the same model. Nova is almost 2× faster.

---

## Qwen 2.5 3B Instruct

**Model:** VRxiaojie/Qwen2.5-3B-Instruct-RKLLM  
**File Size:** ~3.5 GB  
**Prompts:** State capitals list + reverse engineering workflow

### Test 1: 1024 max tokens
- **Speed:** 6.94 tokens/second
- **Output:** 444 tokens
- **Duration:** 63.95 seconds

### Test 2: 2048 max tokens (Stress Test)
- **Speed:** 7.11 tokens/second
- **Output:** 1018 tokens
- **Duration:** 143.11 seconds

### Resource Usage
- **RAM:** 4.0 GiB flat (no spikes during 143s sustained run)
- **NPU:** 68% average, 66-70% range
- **CPU:** ~0-5% idle

### Quality
- Got all 50 state capitals right. 100%.
- Technical explanations were coherent and accurate
- No hallucinations that I could spot
- For comparison, DeepSeek 1.5B only got like 30-35 right

40% slower than DeepSeek but actually gives useful answers. This is the sweet spot for practical use.

### vs Pi 5
Pi 5 does about 2 tok/s on Phi 3.5 3.8B. Nova is 3.5× faster on a similar size model.

---

## DeepSeek-R1-Distill-Qwen-1.5B

**Model:** Pelochus/deepseek-R1-distill-qwen-1.5B  
**File Size:** ~2.0 GB  

### Performance Summary
| Test | Max Tokens | Speed | Output | Duration | NPU Avg |
|------|-----------|-------|--------|----------|---------|
| 1 | 256 | 11.73 t/s | 267 tokens | 22.77s | N/A |
| 2 | 512 | 11.65 t/s | 533 tokens | 45.77s | N/A |
| 3 | 1024 | 11.53 t/s | 1075 tokens | 93.27s | 65% |
| 4 | 2048 | 11.32 t/s | 1885 tokens | 166.45s | 60% |

### Resource Usage
- **RAM:** 2.6 GiB stable (no spikes)
- **NPU:** 58-68% depending on token count
- **Consistency:** 11.32-11.73 t/s across 7.3× output range

### Quality Notes
- Only got 30-35 state capitals right (60-70%)
- Got repetitive, made up some city names
- Fine for speed testing but wouldn't actually use it for anything real

---

## Cross-Model Analysis

### Speed vs. Size Scaling
| Model | Size | Speed | Efficiency (t/s per GB) |
|-------|------|-------|------------------------|
| DeepSeek 1.5B | 2.0 GB | 11.5 t/s | 5.75 |
| Qwen 3B | 3.5 GB | 7.0 t/s | 2.00 |
| Llama 8B | 8.6 GB | 3.72 t/s | 0.43 |

**Takeaway:** Speed doesn't scale linearly. Doubling the model size costs you more than half your speed.

### NPU Utilization Patterns
- **1.5B model:** 60% avg (underutilized)
- **3B model:** 68% avg (good balance)
- **8B model:** 79% avg (near-optimal load)

**Takeaway:** Bigger models push the NPU harder (makes sense). But 3B is probably the best balance of speed and quality.

### RAM Efficiency
All models load entirely in RAM with comfortable headroom:
- 1.5B: 2.6 GiB (16% of available)
- 3B: 4.0 GiB (25% of available)
- 8B: 8.6 GiB (54% of available)

**Note:** 16GB is sufficient for 8B models. Larger models (13B+) would require swap.

---

## vs. Raspberry Pi 5

### Direct Comparisons
| Metric | Nova 3B | Pi 5 3.8B | Nova 8B | Pi 5 8B |
|--------|---------|-----------|---------|---------|
| **Speed** | 7.0 t/s | ~2 t/s | 3.72 t/s | ~2 t/s |
| **RAM** | 4.0 GB | ~5 GB + swap | 8.6 GB | Requires swap |
| **Hardware** | NPU | CPU only | NPU | CPU only |
| **Advantage** | **3.5×** | — | **1.9×** | — |

### The 3B Sweet Spot
Nova runs a **smarter 3B model** at the same speed Pi 5 runs a **dumber 1.5B model**:
- Nova Qwen 3B: 7 t/s, 50/50 capitals ✓
- Pi 5 TinyLlama 1.5B: ~6-8 t/s, questionable accuracy

**This is the killer stat for the article.**

---

## Thermal Performance

**Observation:** No thermal throttling observed during any test.
- Longest sustained run: 166 seconds (DeepSeek 2048 tokens)
- Ambient temp: ~22°C (room temperature)
- Board has passive heatsink + active fan

**Note:** Formal thermal testing (temp sensors, longer runs) pending.

---

## What I Learned

1. **NPU acceleration actually works** — 2-3× faster than Pi 5 across the board
2. **3B is the sweet spot** — 7 tok/s with good accuracy and low RAM
3. **8B is usable** — 3.72 tok/s is fine for interactive stuff (Pi 5 struggles at 2 tok/s)
4. **16GB matters** — 8B runs without swap, which is huge
5. **Chat templates matter** — forgot this once, got gibberish
6. **Runtime versions matter** — old models won't load, wasted an hour on this

---

## Test Prompt

```
List all 50 US state capitals in alphabetical order by state name.
```

Used this because it's easy to verify—either it got them right or it didn't. Also exposes hallucinations fast since you can just count the capitals.

---

## How I Collected This

Ran `monitor-npu.sh` in one terminal to log NPU/RAM every second, ran rkllm in another terminal with the same prompts each time. Pulled the numbers out of the logs afterward and deleted the raw files once I had what I needed.
