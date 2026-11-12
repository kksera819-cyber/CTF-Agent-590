# CTF-Agent-590

## Overview

This project develops and evaluates an LLM-based agent for solving CTF challenges. The goal is to compare a baseline agent with an improved agent and investigate whether tool-assisted reasoning can improve verified challenge-solving performance.

The experiments use the CTFTiny benchmark and GPT-4.1 Mini through the Duke-provided model gateway.

## Architecture

The project contains two agent configurations:

**Baseline Agent**
- Reads allowed challenge files.
- Uses the language model to analyze challenge content.
- Submits candidate flags for verification.
- Does not have access to the Python execution tool.

**Improved Agent**
- Reads challenge descriptions and contestant files.
- Uses isolated Python execution for calculations and reverse engineering.
- Supports machine-code disassembly with Capstone.
- Uses challenge-specific reasoning instructions.
- Submits candidate flags to the trusted evaluator.
- Enforces execution time, step, and token limits.

The evaluator verifies candidate flags separately from the agent. The agent does not receive hidden reference answers.

## Requirements

- Python 3.11
- Docker
- Access to the configured Duke model gateway
- CTFTiny benchmark dataset

Python dependencies are recorded in `requirements.lock.txt`.

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.lock.txt
```

Build the Docker image used by the Python execution tool:

```powershell
docker build -f Dockerfile.ctf -t ctf-python-tool .
```

Configure the model gateway using a local `.env` file containing:

```text
DUKE_MODEL=<model-name>
DUKE_API_BASE=<gateway-url>
LITELLM_TOKEN=<your-token>
```

Do not commit API credentials to the repository.

## Challenge Setup

The project uses the CTFTiny dataset.

Place the benchmark files in the `benchmark/` directory.

The `setup_challenge.py` script stages the contestant files into `agent-workspace/`.

The current setup script selects `rev-baby-mult` through its `CHALLENGE_ID` variable. To stage `rev-checker`, change that variable before running the script.

```powershell
python setup_challenge.py
```

## Running the Agents

### Baseline

```powershell
python agent_runner.py --challenge rev-baby-mult --max-steps 12 --max-seconds 120
```

### Improved

```powershell
python agent_runner_improved.py --challenge rev-baby-mult --max-steps 12 --max-seconds 120 --max-input-tokens 24000 --max-context-chars 20000 --max-response-tokens 1800 --max-idle-turns 3
```

The experiment records the run ID, challenge ID, verification result, execution time, token usage, model calls, tool calls, and trace location.

## Evaluation

Two reversing challenges were selected:

- `rev-checker`
- `rev-baby-mult`

Each configuration was evaluated three times per challenge.

| Challenge | Baseline Success | Improved Success |
|---|---|---|
| rev-checker | 0/3 | 3/3 |
| rev-baby-mult | 0/3 | 3/3 |
| Total | 0/6 | 6/6 |

The improved agent achieved a 100% verified success rate across the six selected runs, compared with 0% for the baseline.

The improved agent also required more model calls, tokens, and execution time.

Detailed results are available in:

- `experiment_results/selected_final_12_runs.csv`
- `experiment_results/final_evaluation_metrics.csv`

## Failure Analysis

During development, the improved agent sometimes failed because of incorrect arithmetic interpretation, Python syntax errors, and token-budget exhaustion.

For the machine-code challenge, the agent initially had difficulty reconstructing the flag from multiplication results. Additional instructions encouraged the agent to identify independent multiplication chains, account for 64-bit arithmetic, decode integer values as ASCII, and combine fragments in the correct order.

After these changes, the selected final improved runs successfully verified their flags.

## Limitations

The evaluation includes only two challenges and three trials per configuration per challenge. The results do not establish general performance across all CTF categories.

The improved configuration also has higher resource consumption than the baseline. Further testing on additional challenge types would help determine whether the improvement generalizes.

## Security and Reproducibility

The agent operates on staged contestant files. Reference answers are handled by the trusted evaluator and are not exposed as agent tools.

Python execution is isolated using Docker, and the runner enforces resource limits.

The experiment records execution traces and evaluation metrics to support reproducibility.

## External Resources and AI Assistance

This project uses the CTFTiny benchmark and the `nyuctf` Python package.

AI assistance was used during development for debugging, code refinement, and documentation. Experimental outcomes are reported from recorded evaluator results rather than assumed model answers.

## Project Files

- `agent_runner.py` — baseline entry point
- `agent_runner_improved.py` — improved entry point
- `ctf_runner_core.py` — shared agent execution logic
- `docker_python_tool.py` — isolated Python execution
- `setup_challenge.py` — challenge staging
- `Dockerfile.ctf` — Docker environment
- `requirements.lock.txt` — Python dependency versions
- `experiment_results/` — experiment data
- `traces/` and `traces_improved/` — execution traces

## References

CTFTiny: https://github.com/NYU-LLM-CTF/CTFTiny

CTFJudge: https://github.com/NYU-LLM-CTF/CTFJudge