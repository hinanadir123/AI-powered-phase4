# Cost Analysis

Analyze and optimize cloud infrastructure costs.

## Usage
```
/cost-analysis [scope]
```

## Arguments
- `scope` (optional): Analysis scope (cluster/namespace/workload/all). Default: all

## What it does
1. Analyzes resource usage and costs
2. Identifies cost optimization opportunities
3. Shows resource allocation vs actual usage
4. Recommends right-sizing for pods
5. Identifies idle resources
6. Generates cost report with savings recommendations

## Example
```
/cost-analysis
/cost-analysis namespace
/cost-analysis workload
```
