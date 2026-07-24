from __future__ import annotations

from time import perf_counter

from agent_arena_api.benchmark_seed import BENCHMARK_OWNER, seed_benchmark_database
from agent_arena_api.database import Database
from agent_arena_api.models import Agent, Base, Fixture, Submission
from isolation_engine import BENCHMARK_STRATEGY_LIST, BenchmarkController, Isolation
from sqlalchemy import func, select


def test_benchmark_catalog_is_deliberate_and_unique() -> None:
    assert len(BENCHMARK_STRATEGY_LIST) == 15
    assert len({strategy.key for strategy in BENCHMARK_STRATEGY_LIST}) == 15
    assert len({strategy.agent_name for strategy in BENCHMARK_STRATEGY_LIST}) == 15
    assert {strategy.mode for strategy in BENCHMARK_STRATEGY_LIST} == {
        "random",
        "weighted",
        "greedy",
        "fixed",
        "iterative",
    }
    assert {strategy.evaluation for strategy in BENCHMARK_STRATEGY_LIST} == {
        "mobility",
        "differential",
        "center",
        "territory",
        "partition",
    }


def test_every_benchmark_strategy_returns_a_legal_action_within_budget() -> None:
    state = Isolation().result(57).result(0)
    for strategy in BENCHMARK_STRATEGY_LIST:
        controller = BenchmarkController(strategy.key, seed=17)
        controller.reset(state.player())
        started = perf_counter()
        response = controller.choose_action(state, timeout_ms=150)
        elapsed_ms = (perf_counter() - started) * 1000
        assert response.action in state.actions(), strategy.agent_name
        assert elapsed_ms < 200, strategy.agent_name


def test_benchmark_seed_is_isolated_and_does_not_create_fixtures(tmp_path) -> None:
    normal = Database.create(f"sqlite:///{(tmp_path / 'normal.db').as_posix()}")
    benchmark = Database.create(f"sqlite:///{(tmp_path / 'benchmark.db').as_posix()}")
    Base.metadata.create_all(normal.engine)
    Base.metadata.create_all(benchmark.engine)

    result = seed_benchmark_database(benchmark)
    assert result == {"agents": 15, "submissions": 15, "fixtures": 0}
    assert seed_benchmark_database(benchmark) == result

    with normal.sessions() as session:
        assert session.scalar(select(func.count(Agent.id))) == 0
    with benchmark.sessions() as session:
        assert set(session.scalars(select(Agent.owner_name))) == {BENCHMARK_OWNER}
        assert set(session.scalars(select(Submission.execution_kind))) == {
            strategy.key for strategy in BENCHMARK_STRATEGY_LIST
        }
        assert session.scalar(select(func.count(Fixture.id))) == 0

    normal.engine.dispose()
    benchmark.engine.dispose()
