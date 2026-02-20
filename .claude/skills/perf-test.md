# Performance Test

Run performance tests and profiling on the Todo AI Chatbot.

## Usage
```
/perf-test [component] [type]
```

## Arguments
- `component` (optional): Component to test (backend/frontend/database/all). Default: all
- `type` (optional): Test type (cpu/memory/latency/throughput). Default: all

## What it does
1. Runs performance benchmarks
2. Profiles CPU and memory usage
3. Measures API latency
4. Tests database query performance
5. Generates performance report with recommendations

## Example
```
/perf-test
/perf-test backend cpu
/perf-test database latency
```
