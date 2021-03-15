# History

## v0.3.0 (2021-03-14)

- Added HISTORY.md file
- Changed import syntax to `from pandas_path import path` to better support custom accessors. This means that we do not register `.path` unless you import `.path` so that in other libraries you don't have to add the `.path` accessor if you are just registering your own custom accessor.
- Added quickstart section to README
- Fix bug where we tried to instantiate with blank string for an example rather than first item in the Series
