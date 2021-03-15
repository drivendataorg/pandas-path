from pathlib import Path

from ..accessor import register_path_accessor  # noqa


register_path_accessor("path", Path)
