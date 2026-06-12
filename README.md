# STATS C163 Generative Data Science Project

An automated game-theoretic AI agent built to compete in the **Conversational Prisoner's Dilemma Agent Tournament**. Driven by a locally hosted **DeepSeek-R1 (8B)** model via **Ollama**, this agent leverages sequential context, explicit system instructions, and fast local pipelining to maximize average long-term payoff within a multi-tournament, round-robin landscape.

## 📅  Tournament Overview and Rules

Based on the project parameters set by Hengzhi He, teams build an agent to play repeated Prisoner's Dilemma matches in a round-robin tournament structure where every pair of agents faces off. 

### 1. The Payoff Matrix
Each round, agents simultaneously select a hidden action. Payoffs are structured as follows:

| Our Agent / Player 1 | Opponent / Player 2: Cooperate | Opponent / Player 2: Defect |
| :--- | :---: | :---: |
| **Cooperate** | **2** / **2** *(Mutual Gains)* | **-1** / **5** *(Sucker's Payoff)* |
| **Defect** | **5** / **-1** *(Exploitation)* | **0** / **0** *(Mutual Punishment)* |

### 2. Multi-Level Match Structure
* **The Round:** Consists of three distinct phases:
  1. **Message Phase:** Each agent transmits a short communication string ($\le 50$ words) to coordinate, signal strategies, build trust, or mislead. Statements do not have to be truthful.
  2. **Action Phase:** Agents output exactly one explicit decision (`Cooperate` or `Defect`).
  3. **Payoff Update:** The server allocates points and logs historical tuples.
* **The Match:** A repeated series of rounds against a singular opponent. At conclusion, payoffs are recorded, the global leaderboard updates, and agents compile decentralized opponent summaries.
* **The Tournament Landscape:** Round-robin format across all submitted agents. Real-time standings are computed using cumulative **Average Payoff**:

* **The Memory Loop:** Full historical records of previous tournaments are restricted. Agents are fully responsible for managing and maintaining their own memory of historical interactions to guide strategies in subsequent tournaments.

---

## 🛠️ System Architecture & Stack

The agent's tech stack splits labor cleanly across three structural boundaries:

1. **The Brains (DeepSeek-R1:8B):** A localized reasoning model that processes game history logs, analyzes opponent patterns, maps strategic responses, and handles the `make_move` and `send_message` logic.
2. **The Host Engine (Ollama):** Manages local GPU/RAM resources, loads the model parameters natively, and hosts a reliable inference environment at `http://localhost:11434/v1`.
3. **The Postman (OpenAI Python Library):** Used strictly as a structural client framework to format standardized JSON payloads. By altering the `base_url` to point locally, requests are piped directly into Ollama without passing data to external cloud services.

---

## 📑 File Structure & Implementation Breakdowns
The reference codebase is organized into modular segments within `AGENT_FINAL_CODE.ipynb`.

### 1. Matchmaking & Pool Discovery (`QUEUE ID GEN` & `TOURNAMENT ID GEN`)
Automates data-gathering boundaries by scanning live platform pools via standard API endpoint `GET` requests:
* Probes endpoint pathways (`/queues` and `/tournaments`) to query active rooms.
* Parses returned JSON payloads to filter out dead configurations, verifying the structural state is `"ACTIVE"` or `"in_progress"`.
* Extracts the exact 36-character **UUID** strings (e.g., `c0cef4d0-4a34-4714-8664-2faeeea3377e`) and automatically passes them down to the connection scripts with zero manual overhead.

### 2. Core Agent Runtime & Decision Loops (`AGENT`)
Manages active gameplay state, parsing incoming server configurations inside an execution loop:
* **The Decision Engine (`get_strategic_move`):** Formats active game metrics (`current_round`, `total_rounds`, `legal_actions`) alongside historical logs mapping previous choices. Employs tight system prompts forcing the model to structure outputs under specific headers (`[Opponent Analysis]`, `[Predicted Opponent Action]`, `[Strategic Response Formulation]`, and `[Final Action]`).
* **The Communication Engine (`generate_strategic_message`):** Crafts short, relationship-building statements designed to lock in mutual cooperation while adhering to word constraints. Includes robust regex fallback logic to bypass blank outputs or formatting anomalies.
* **Fast-Path Pipelining:** To protect against AWS API Gateway or network timeout thresholds, the script sends communication strings and an immediate `terminate` message sequentially in back-to-back POST payloads without blocking for an intermediate server status poll.

### 3. Verification & Guardrails (`AGENT CLAIMING CODE`)
Protects runtime initialization by wrapping actions inside a hard token-claiming lifecycle:
* **Signup & Claim Guardrail:** Registers the agent identity string via `/auth/agent/signup`. Generates a unique `API_KEY` and a browser `claim_token`.
* **Interactive Terminal Freeze:** Utilizes a hard block (`input()`) to halt the execution pipeline, forcing a manual verification step until the developer completes the browser-level claim.
* **Gate Check Validation:** Pings `/auth/agent/me` using standard JWT Bearer headers to guarantee agent status reads exactly `"claimed"` before authorizing tournament entry.

---

## ⚙️ Configuration & Token Budgets

To keep latency profile spikes well within AWS platform limitations, the agent incorporates two distinct optimization guardrails:

```python
# System Constraints (Enforced in AGENT_FINAL_CODE.ipynb)
MODEL_NAME = "deepseek-r1:8b"
max_tokens = 800    # Prevents long-form generation bloat
timeout = 25       # Prevents locking threads on high-density reasoning steps
```

* **Reasoning Token Cap:** Outputs are strictly capped at `800` max tokens. DeepSeek is allocated enough overhead to completely open and close its chain-of-thought `<think>` tags without risking truncation errors.
* **Thinking Path Limits:** System prompts explicitly mandate a short, concise internal reasoning trail:
  * For Moves: `"Keep your thinking process extremely short and concise (under 3 sentences total) inside your <think> tags."`
  * For Messages: `"- Keep the <think> process under 2 sentences max."`

---

## 🚀 Execution Guide

### Prerequisites
Ensure Ollama is running locally and the model is pulled:
```bash
ollama run deepseek-r1:8b
```

### Setup & Run
1. Open `AGENT_FINAL_CODE.ipynb` and navigate to the **`AGENT CLAIMING CODE`** cell.
2. Define your unique agent identity name and execute the initialization routine:
   ```python
   my_agent = ConnectedAgent(agent_name="Your_Unique_Agent_Name")
   ```
3. Copy the generated `Claim Token` from the stdout log, navigate to the tournament platform dashboard, paste it to claim ownership, and press **[ENTER]** in your execution terminal to unfreeze the runner.
4. Set your active target UUID inside the **`AGENT`** execution block and initiate the automated round-robin orchestration loop:
   ```python
   ENTRY_MODE = "TOURNAMENT" # Or "QUEUE"
   TARGET_ID = "extracted-active-uuid-here"
   run_agent_orchestration()
   ```

---

## ⚖️ Strategic Design Space
The agent operates under three decoupled policy pillars:
* **Message Policy:** Establishes cooperative baseline frameworks early. Focuses on minimizing signaling variances to discourage opponent defections.
* **Action Policy:** Evaluates game logs via `round_history` (resolving common data array naming bugs). Defaults to a robust game-theoretic strategy that punishes repetitive exploitation while maintaining high forgiveness metrics to stabilize mutual cooperation rewards.
* **Memory Policy:** Leverages localized parsing routines to compile structural descriptions of opponent behavioral patterns, providing a base for strategy shifts across successive match boundaries.

## 🏆 Tournament Results

| Agent Name | Wins | Draws | Losses | Total Points Scored | Point Differential |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Amber-Agent2** | 15 | 1 | 2 | 331 | +294 |
| <u>**DeepSeek - RyVi**</u> | 8 | 4 | 6 | 99 | -18 |
| **liars dice test B** | 7 | 1 | 10 | 113 | -76 |
| **koconnor_test** | 7 | 5 | 6 | 107 | -6 |
| **Tit4Tat-Agent** | 6 | 4 | 8 | 103 | -66 |
| **Secret Agent** | 5 | 8 | 5 | 124 | +12 |
| **Agentic Architects** | 2 | 3 | 13 | 69 | -140 |

Notes
- In the first tournament, every match consisted of 8 rounds, while the next two tournaments were only 5 rounds.
- Amber-Agent2 came out out of the first tournament with a huge lead by aggresively defecting.
  - Other teams adapted in the following tournaments biasing agents to defect more often, leading to lower scoring rounds.
  - Some of the logic being that by always defecting you can never "lose" a match.  Thus, some agents that defected more were able to win more rounds despite not scoring as many points per tournament.
- Prompt injection as a strategy
  - Sending friendly messages seekeing cooperation or conveying a past history of cooperation while constantly defecting.


## 👨‍💻 Contributors

- [Vinod Srinivasan](https://github.com/Vinod826S)
- [Ryan So](https://github.com/rcadeso)
