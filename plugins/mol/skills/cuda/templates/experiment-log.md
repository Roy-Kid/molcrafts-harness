# Experiment log — `<kernel or feature>`

- **GPU:**
- **CUDA / driver:**
- **Problem size(s):**
- **Dtype:**
- **Benchmark command:**
- **Correctness command:**

## Iterations

| iteration | optimization | time | metric | correctness | bottleneck | evidence | status |
|----------:|:-------------|-----:|-------:|:------------|:-----------|:---------|:-------|
| 0 | baseline |  |  | PASS/FAIL |  |  | keep |
| 1 |  |  |  |  |  |  | keep/revert |

## Notes

- Decision rules: fail correctness → revert; prefer keep when ≥5% stable gain;
  stop after repeated <2% gains unless user requests more.
- Never log a keep without a correctness PASS for that iteration.
