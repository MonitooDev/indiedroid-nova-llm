#!/usr/bin/env python3
"""
RKLLM Benchmark Runner for Indiedroid Nova
Runs inference and logs performance metrics (tokens/s, RAM, NPU usage)

Usage:
    python3 run-benchmark.py <model.rkllm> [options]

Example:
    python3 run-benchmark.py ~/models/Llama-3.1-8B.rkllm --max-tokens 1024 --prompt "List capitals"
"""

import subprocess
import sys
import time
import argparse
import os
import csv
from datetime import datetime
from pathlib import Path


def check_rkllm_available():
    """Check if rkllm binary is available"""
    try:
        result = subprocess.run(['which', 'rkllm'], capture_output=True, text=True)
        if result.returncode != 0:
            print("ERROR: 'rkllm' binary not found in PATH")
            print("Please run setup-nova.sh first or install ezrknn-llm manually")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR checking for rkllm: {e}")
        sys.exit(1)


def get_ram_usage():
    """Get current RAM usage in GB"""
    try:
        result = subprocess.run(['free', '-g'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        mem_line = [l for l in lines if l.startswith('Mem:')][0]
        used = int(mem_line.split()[2])
        total = int(mem_line.split()[1])
        return used, total
    except Exception as e:
        return None, None


def get_npu_load():
    """Get current NPU load across all cores"""
    try:
        result = subprocess.run(
            ['sudo', 'cat', '/sys/kernel/debug/rknpu/load'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return "N/A"


def parse_chat_template(prompt, model_name):
    """
    Apply chat template based on model type
    Returns formatted prompt string
    """
    model_lower = model_name.lower()
    
    # Llama 3.1 template
    if 'llama-3' in model_lower or 'llama3' in model_lower:
        return f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    
    # Qwen template
    elif 'qwen' in model_lower:
        return f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
    
    # Default: no template
    else:
        return prompt


def run_benchmark(model_path, prompt, max_tokens=1024, max_context=4096, apply_template=True):
    """
    Run RKLLM inference and capture performance metrics
    
    Returns dict with:
        - tokens_per_second
        - total_tokens
        - duration_seconds
        - ram_used_gb
        - npu_load
    """
    
    if not os.path.exists(model_path):
        print(f"ERROR: Model file not found: {model_path}")
        sys.exit(1)
    
    model_name = os.path.basename(model_path)
    print(f"\n{'='*60}")
    print(f"Model: {model_name}")
    print(f"Prompt: {prompt[:50]}...")
    print(f"Max tokens: {max_tokens}, Max context: {max_context}")
    print(f"{'='*60}\n")
    
    # Apply chat template if enabled
    if apply_template:
        formatted_prompt = parse_chat_template(prompt, model_name)
        print(f"Applied chat template for {model_name}")
    else:
        formatted_prompt = prompt
    
    # Get baseline metrics
    ram_before, ram_total = get_ram_usage()
    npu_before = get_npu_load()
    
    print(f"Baseline RAM: {ram_before}GB / {ram_total}GB")
    print(f"Baseline NPU: {npu_before}")
    print(f"\nStarting inference...")
    
    # Run rkllm
    start_time = time.time()
    
    try:
        # Note: rkllm is interactive, so we'd need to automate input
        # For now, this shows the command structure
        cmd = ['rkllm', model_path, str(max_tokens), str(max_context)]
        print(f"\nCommand: {' '.join(cmd)}")
        print(f"Prompt to paste: {formatted_prompt}\n")
        print("NOTE: This script shows the setup. For actual benchmarking,")
        print("run rkllm manually and use monitor-npu.sh in another terminal.")
        print("\nManual steps:")
        print(f"  Terminal 1: ./monitor-npu.sh {model_name.replace('.rkllm', '')}_benchmark.log")
        print(f"  Terminal 2: rkllm {model_path} {max_tokens} {max_context}")
        print(f"  Then paste: {formatted_prompt}")
        
        return None
        
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
        sys.exit(0)


def save_results(results, output_csv='benchmark_results.csv'):
    """Save benchmark results to CSV"""
    fieldnames = ['timestamp', 'model', 'tokens_per_second', 'total_tokens', 
                  'duration_seconds', 'ram_used_gb', 'npu_load', 'prompt']
    
    file_exists = os.path.exists(output_csv)
    
    with open(output_csv, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(results)
    
    print(f"\n✓ Results saved to {output_csv}")


def main():
    parser = argparse.ArgumentParser(
        description='Run RKLLM benchmark on Indiedroid Nova',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run-benchmark.py model.rkllm --prompt "What is AI?"
  python3 run-benchmark.py model.rkllm --max-tokens 2048 --no-template
        """
    )
    
    parser.add_argument('model', help='Path to .rkllm model file')
    parser.add_argument('--prompt', default='List all 50 US state capitals in alphabetical order by state name.',
                        help='Prompt for inference (default: state capitals)')
    parser.add_argument('--max-tokens', type=int, default=1024,
                        help='Maximum tokens to generate (default: 1024)')
    parser.add_argument('--max-context', type=int, default=4096,
                        help='Maximum context length (default: 4096)')
    parser.add_argument('--no-template', action='store_true',
                        help='Disable automatic chat template formatting')
    parser.add_argument('--output', default='benchmark_results.csv',
                        help='Output CSV file (default: benchmark_results.csv)')
    
    args = parser.parse_args()
    
    # Validate environment
    check_rkllm_available()
    
    # Run benchmark
    results = run_benchmark(
        args.model,
        args.prompt,
        args.max_tokens,
        args.max_context,
        apply_template=not args.no_template
    )
    
    # Note: Currently this is a helper script that shows the setup
    # Actual benchmarking needs manual interaction with rkllm CLI
    

if __name__ == '__main__':
    main()
