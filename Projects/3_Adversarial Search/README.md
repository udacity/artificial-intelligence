# Agent Arena

Agent Arena is a local browser-based beta for one permanent Knight Isolation competition.

> Submit once. Your Knight Isolation agent keeps competing.

The beta deliberately uses a small architecture: React calls FastAPI over HTTP; FastAPI uses SQLAlchemy with one SQLite file; the authoritative Python engine runs games; and submitted source is imported only inside a Docker container. Rankings are calculated directly from completed games instead of being cached in a separate standings table.

## What the product does

- Edit and practice one `agent.py` against Random, Greedy, or Minimax.
- Validate syntax, the public contract, representative legal actions, and one Greedy scrimmage.
- Store only accepted immutable submissions.
- Automatically make the newest accepted submission active.
- Run one mirrored fixture for every pair of active submissions.
- Award 3/1/0 fixture points and rank qualified agents by points per fixture.
- Replay both games in a completed fixture.
- Open a subordinate Agent page for immutable submissions and complete fixture history.

There are five browser views: Overview, Code & Play, Leaderboard, My Agents, and Submit Agent. There is no rating system, calendar, season, event system, payment system, or production authentication.

The leaderboard marks an active submission as provisional until it has played 10 fixtures by default. Qualified entries are ordered by points per fixture (PPF), then raw points, fixture wins, and agent name. The threshold can be changed with `AGENT_ARENA_MINIMUM_RANKED_FIXTURES`; the formula and qualification state are returned by the API.

## Prerequisites

- Python 3.12.x
- Node.js 22.17.0 and npm
- Docker Engine or Docker Desktop for submitted-source execution
- GNU Make on Linux/macOS; PowerShell commands are provided for Windows

Docker is optional for browsing seeded results and running trusted baseline rounds. It is mandatory for practice or competition with submitted source. The API never falls back to importing submitted source.

## Database reset after the simplification refactor

The simplified schema intentionally replaces the earlier local-beta schema. Existing data is not deleted automatically.

If `var/agent_arena.db` was created by the earlier architecture, rename it before setup:

```powershell
Move-Item var\agent_arena.db var\agent_arena_before_simplification.db
```

On Linux/macOS:

```bash
mv var/agent_arena.db var/agent_arena_before_simplification.db
```

The old database remains available as a backup but is not read by the simplified application.

## Linux/macOS quick start

```bash
cp .env.example .env
make setup
make runner-build
make dev
```

Open:

- Web app: http://127.0.0.1:5173
- API health: http://127.0.0.1:8000/api/health
- OpenAPI: http://127.0.0.1:8000/docs

`make setup` creates the virtual environment, installs pinned dependencies, applies the one Alembic migration, and seeds four trusted demo agents plus completed fixtures.

## Windows PowerShell

```powershell
Copy-Item .env.example .env
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
npm.cmd ci --prefix apps\web
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\agent-arena.exe seed
docker build -f packages\agent_runner\Dockerfile -t agent-arena-runner:py312-v1 .
.\.venv\Scripts\python.exe scripts\dev.py
```

This checkout may be inspected with another Python version, but the supported application and runner runtime is Python 3.12.

## Agent contract

Submit one file named `agent.py`:

```python
class CustomPlayer:
    def get_action(self, state):
        actions = state.actions()
        return actions[0] if actions else None
```

The original queue style is also supported:

```python
self.queue.put(action)
```

The player may use `self.context` during one game. A fresh container and player instance are created for the next game. The trusted engine always validates the proposed action against `state.actions()`.

## Simple data model

- **Agent**: stable name and owner identity.
- **Submission**: immutable accepted source; the newest accepted submission is active.
- **Fixture**: one pair of mirrored games.
- **Game**: one result and one canonical replay list.

There is no Standing table. The leaderboard is recalculated from completed Fixtures and Games whenever it is requested.

## Common commands

```bash
make dev           # launch the normal development database
make benchmark     # launch with the isolated 15-agent benchmark database
make seed          # idempotently create demo agents and initial fixtures
make run-round     # synchronously run one balanced all-active round
make test          # backend and frontend formatting, lint, tests, and build
make clean-start   # start temporary API/web ports and probe both
make runner-build  # build the local Python 3.12 runner image
```

On Windows, launch benchmark mode with:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark.py
```

Stop the normal development servers first because both modes use ports 5173 and 8000. Benchmark mode applies the same migration and seeds 15 trusted strategy variants into `var/benchmark/agent_arena.db`; it does not read, seed, or modify `var/agent_arena.db`. Open the Leaderboard and click **Run competition round**. One 15-agent round runs 105 mirrored fixtures (210 games), gives every agent 14 fixtures, and therefore clears the default 10-fixture ranking threshold.

The CLI intentionally contains only three commands:

```bash
agent-arena doctor
agent-arena seed
agent-arena run-round
```

`doctor` checks whether the database file and Docker runner image exist without creating a schema.

## Repository map

```text
apps/web                    React browser interface
apps/api                    FastAPI routes, SQLAlchemy, Alembic, operations
packages/isolation_engine   authoritative state, baselines, game, replay, scoring
packages/agent_runner       Docker coordinator, worker, queue compatibility
tests                       focused backend and API flow tests
docs                        architecture, API, security, limits, learning map
```

## Testing

```powershell
.\.venv\Scripts\ruff.exe format --check apps packages scripts tests
.\.venv\Scripts\ruff.exe check apps packages scripts tests
.\.venv\Scripts\pytest.exe
npm.cmd run lint --prefix apps\web
npm.cmd run typecheck --prefix apps\web
npm.cmd test --prefix apps\web -- --run
npm.cmd run build --prefix apps\web
.\.venv\Scripts\python.exe scripts\startup_check.py
```

The main API acceptance path is `tests/integration/test_api.py::test_submit_practice_compete_leaderboard_and_replay`. It uses a controller test double so it can run without Docker. A real submitted-source run still requires the built Docker image.

## Security scope

This is a local beta, not a production multi-tenant sandbox. Do not expose it to arbitrary internet users. Docker reduces risk but does not eliminate kernel, daemon, denial-of-service, side-channel, or supply-chain risks.

The original engine encoding details remain available in
[the Isolation library guide](isolation/README.md).
