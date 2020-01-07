# `pandas_path` - Path style access for pandas

 [![PyPI](https://img.shields.io/pypi/v/pandas-path.svg)](https://pypi.org/project/pandas-path/)

Love [`pathlib.Path`]()*? Love pandas? Wish it were easy to use pathlib methods on pandas Series?

This package is for you. Just one import adds a `.path` accessor to any pandas Series or Index so that you can use all of the methods on a `Path` object.

<small> * If not, you should.</small>

Here's an example:

```python
from pathlib import Path
import pandas as pd

# This is the only line you need to register `.path` as an accessor
# on any Series or Index in pandas.
import pandas_path

# we'll make an example series from the py files in this repo;
# note that every element here is just a string--no need to make Path objects yourself
file_paths = pd.Series(str(s) for s in Path().glob('**/*.py'))

# 0                   setup.py
# 1    pandas_path/accessor.py
# 2        pandas_path/test.py
# dtype: object
```

Use the `.path` accessor to get just the filename rather than the full path:

```python
file_paths.path.name

# 0       setup.py
# 1    accessor.py
# 2        test.py
# dtype: object
```

Use the `.path` accessor to get just the parent folder of each file:

```python
file_paths.path.parent

# 0              .
# 1    pandas_path
# 2    pandas_path
# dtype: object
```

Use calculated methods like `exists` to filter for what exists on the filesystem:

```python
file_paths.loc[3] = 'fake_file.txt'

# 0                   setup.py
# 1    pandas_path/accessor.py
# 2        pandas_path/test.py
# 3              fake_file.txt
# dtype: object

file_paths.path.exists()

# 0     True
# 1     True
# 2     True
# 3    False
# dtype: bool
```

Use path methods like `with_suffix` to dynamically create new filenames:

```python
file_paths.path.with_suffix('.png')

# 0                   setup.png
# 1    pandas_path/accessor.png
# 2        pandas_path/test.png
# 3               fake_file.png
# dtype: object
```

Use the `/` operators just as you would in `pathlib` (with the `.path` accessor on either side of the operator.)

```python
"different_root_folder" / file_paths.path

# 0                   different_root_folder/setup.py
# 1    different_root_folder/pandas_path/accessor.py
# 2        different_root_folder/pandas_path/test.py
# dtype: object
```

We'll even do element wise operations with lists/arrays/series of the same length.

```python
file_paths.path.parent.path / ["other_file1.txt", "other_file2.txt", "other_file3.txt"]

# 0                other_file1.txt
# 1    pandas_path/other_file2.txt
# 2    pandas_path/other_file3.txt
# dtype: object
```

### Limitations

1. While most operations work out of the box, operator chaining with `/` will not work as expected since we always return the series itself, not the accessor.

```python
file_paths.path.parent.path / "subfolder" / "other_file1.txt"

# ----> 1 file_paths.path.parent.path / "subfolder" / "other_file1.txt"
# ...
# TypeError: unsupported operand type(s) for /: 'str' and 'str'

```

Instead, either use the `.path` accessor on the result or re-write without chaining:

```python

(file_paths.path.parent.path / "subfolder").path / "other_file1.txt"

# 0                subfolder/other_file1.txt
# 1    pandas_path/subfolder/other_file1.txt
# 2    pandas_path/subfolder/other_file1.txt
# dtype: object

file_paths.path.parent.path / "subfolder/other_file1.txt"

# 0                subfolder/other_file1.txt
# 1    pandas_path/subfolder/other_file1.txt
# 2    pandas_path/subfolder/other_file1.txt
# dtype: object

```

2. A numpy array or pandas series on the left hand side of `/` will not work properly.


```python
pd.Series(['a', 'b', 'c']) / pd.Series(['1', '2', '3']).path

## IMPROPERLY BROADCASTS :'(

# 0    0    a/1
# 1    a/2
# 2    a/3
# dtype: object
# 1    0    b/1
# 1    b/2
# 2    b/3
# dtype: object
# 2    0    c/1
# 1    c/2
# 2    c/3
# dtype: object
# dtype: object
```

Instead, use the path accessor on the right-hand side as well.

```python
pd.Series(['a', 'b', 'c']).path / pd.Series(['1', '2', '3']).path

# 0    a/1
# 1    b/2
# 2    c/3
# dtype: object
```


That's all folks, enjoy!

Developed and maintained by your friends at DrivenData! [ml competitions](https://www.drivendata.org/) | [ai consulting](http://drivendata.co/)
