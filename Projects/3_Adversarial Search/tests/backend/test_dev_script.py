from __future__ import annotations

from scripts.dev import RELOAD_DIRECTORIES, ROOT, api_command


def test_dev_reloader_watches_source_packages_not_runtime_state() -> None:
    command = api_command()
    watched = [command[index + 1] for index, value in enumerate(command) if value == "--reload-dir"]

    assert watched == [str(directory) for directory in RELOAD_DIRECTORIES]
    assert str(ROOT / "var") not in watched
    assert str(ROOT) not in watched
