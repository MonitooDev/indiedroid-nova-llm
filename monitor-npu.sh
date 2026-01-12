#!/bin/bash
# NPU and RAM monitoring script for RKLLM benchmarks
# Logs NPU utilization and RAM usage every second
# Usage: ./monitor-npu.sh <output_log_file>

OUTPUT_LOG="${1:-benchmark.log}"

echo "Starting NPU and RAM monitoring..."
echo "Logging to: $OUTPUT_LOG"
echo "Press Ctrl+C to stop"
echo ""

# Check if rknpu debug interface is available
if [ ! -f /sys/kernel/debug/rknpu/load ]; then
    echo "ERROR: /sys/kernel/debug/rknpu/load not found"
    echo "Make sure:"
    echo "  1. You're running on RK3588/RK3588S"
    echo "  2. RKNPU driver is loaded"
    echo "  3. You have sudo permissions"
    exit 1
fi

# Create/truncate log file
> "$OUTPUT_LOG"

# Main monitoring loop
while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    NPU_LOAD=$(sudo cat /sys/kernel/debug/rknpu/load 2>/dev/null || echo "NPU load: N/A")
    RAM_USAGE=$(free -h | grep Mem | awk '{print $3 "/" $2}')
    
    echo "$TIMESTAMP | NPU: $NPU_LOAD | RAM: $RAM_USAGE" | tee -a "$OUTPUT_LOG"
    
    sleep 1
done
