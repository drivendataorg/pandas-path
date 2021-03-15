import os
from pathlib import Path, PureWindowsPath
import sys

import numpy as np
import pytest


@pytest.fixture
def unload_pandas():
    del globals()["pd"]
    for m in list(sys.modules.keys()):
        if m.startswith("pandas"):
            del sys.modules[m]


@pytest.fixture
def pd():
    import pandas as pd

    return pd


@pytest.fixture
def pandas_path():
    import pandas_path
    from pandas_path import path  # noqa

    assert pandas_path.__version__ is not None

    return pandas_path


@pytest.fixture
def sample_paths():
    return list(Path().glob("**/*.py"))


@pytest.fixture
def sample_series(pd, pandas_path, sample_paths):
    return pd.Series(str(s) for s in sample_paths)


def test_not_registered(unload_pandas, pd):
    assert not getattr(pd.Series, "path", None)


def test_registered(pd, pandas_path):
    assert getattr(pd.Series, "path", None)


def test_properties(sample_series, sample_paths):
    expected = [Path(f).name for f in sample_paths]
    assert sample_series.path.name.tolist() == expected

    expected = [str(Path(f).parent) for f in sample_paths]
    assert sample_series.path.parent.tolist() == expected

    expected = [str(Path(f).suffix) for f in sample_paths]
    assert sample_series.path.suffix.tolist() == expected

    expected = [str(Path(f).stem) for f in sample_paths]
    assert sample_series.path.stem.tolist() == expected


def test_methods(sample_series, sample_paths):
    # is_file
    expected = [Path(f).is_file() for f in sample_paths]
    assert sample_series.path.is_file().tolist() == expected

    # exists
    expected = [Path(f).exists() for f in sample_paths]

    # append a file that doesn't exist
    with_not_exist = sample_series.copy()
    with_not_exist.loc[-1] = "not_exist.file"
    expected += [False]

    assert with_not_exist.path.exists().tolist() == expected

    # all files except added one are .py
    assert with_not_exist.path.match("*.py").tolist() == expected

    # with_suffix
    expected = [str(Path(f).with_suffix(".png")) for f in sample_paths]
    assert sample_series.path.with_suffix(".png").tolist() == expected

    # with_name
    expected = [str(Path(f).with_name("new.png")) for f in sample_paths]
    assert sample_series.path.with_name("new.png").tolist() == expected


def test_operators(sample_series, sample_paths):
    # left hand
    expected = [str(Path(f).parent / "new_file.txt") for f in sample_paths]
    assert (sample_series.path.parent.path / "new_file.txt").tolist() == expected

    # right hand
    expected = [str("new_root" / Path(f)) for f in sample_paths]
    assert ("new_root" / sample_series.path).tolist() == expected

    # chaining - error
    with pytest.raises(TypeError):
        sample_series.path.parent.path / "new_folder" / "new_file"

    # chaining - explicit
    expected = [str(Path(f).parent / "new_sub_folder" / "new_file.txt") for f in sample_paths]
    assert (
        (sample_series.path.parent.path / "new_sub_folder").path / "new_file.txt"
    ).tolist() == expected

    # left-hand path object (only supported Python > 3.7 because of https://bugs.python.org/issue34775)
    if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
        assert (
            (Path("new_folder") / sample_series.path) == ("new_folder" + os.sep + sample_series)
        ).all()

    # right-hand path object
    assert (
        (sample_series.path.parent.path / Path("new_file.txt"))
        == (
            (sample_series.path.parent.replace(".", "") + os.sep).str.lstrip("." + os.sep)
            + "new_file.txt"
        )
    ).all()


def test_elementwise(pd, sample_series, sample_paths):
    # operators
    to_append = [f"file_{i}.txt" for i in range(len(sample_series))]
    to_prepend = [f"folder_{i}" for i in range(len(sample_series))]

    expected = [str(Path(f).parent / a) for f, a in zip(sample_paths, to_append)]
    assert (sample_series.path.parent.path / to_append).tolist() == expected
    assert (sample_series.path.parent.path / np.array(to_append)).tolist() == expected
    assert (sample_series.path.parent.path / pd.Series(to_append)).tolist() == expected
    assert (sample_series.path.parent.path / pd.Series(to_append).path).tolist() == expected

    expected = [str(p / Path(f)) for f, p in zip(sample_paths, to_prepend)]
    assert (to_prepend / sample_series.path).tolist() == expected
    assert (pd.Series(to_prepend).path / sample_series.path).tolist() == expected

    # These will not work :/
    # assert (np.array(to_prepend) / sample_series.path).tolist() == expected
    # assert (pd.Series(to_prepend) / sample_series.path).tolist() == expected

    # methods
    # with_suffix
    suffixes = np.random.choice([".txt", ".py", ".jpeg"], size=len(sample_series))

    expected = [str(Path(f).with_suffix(s)) for f, s in zip(sample_paths, suffixes)]
    assert sample_series.path.with_suffix(suffixes).tolist() == expected


def test_custom_accessor(pd, sample_paths):
    from pandas_path import register_path_accessor

    register_path_accessor("win", PureWindowsPath)

    win_series = pd.Series(
        [
            "c:\\test\\f1.txt",
            "c:\\test2\\f2.txt",
        ]
    )

    assert (win_series.win.parent == (win_series.str.rsplit("\\", 1).str[0])).all()

    assert win_series.win.__name__ == "PureWindowsPathAccessor"
    assert "PureWindowsPath" in win_series.win.__doc__
