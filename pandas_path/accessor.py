from types import FunctionType, LambdaType, MethodType

import numpy as np
import pandas as pd


def path_accessor_factory(path_class, *args, **kwargs):
    class PathAccessor:
        _doc_str_f = """A `.{accessor_name}` accessor on Series and Index objects so that all of the methods
            from {path_class} are available.

            Note: Always will return a `str` rather than a {path_class} object so that joining with existing
                dataframes, etc. will continue to work.

            Note: May not be performant on extremely long lists since we cast to `{path_class}`
            for every operation.

        Raises
        ------
        AttributeError
            If the method we try to use on the accessor is not a function or property or
            is not an attribute on {path_class}, raise an AttributeError.
        """

        def __init__(self, pandas_obj):
            self._validate(pandas_obj)
            self._obj = pandas_obj

        @staticmethod
        def _validate(obj):
            [path_class(x, *args, **kwargs) for x in obj.values]

        @staticmethod
        def _to_path_object(path_str):
            return path_class(path_str, *args, **kwargs)

        def __getattr__(self, attr):
            # return accessor name for clarity
            if attr == "__name__":
                return self.__class__.__name__

            apply_series = self._obj.to_series() if isinstance(self._obj, pd.Index) else self._obj

            # check the type of this attribute on a Path object (we need an actual instance) since
            # the super classes dispatch
            if isinstance(self._obj.values[0], path_class):
                attr_type = getattr(type(self._obj.values[0]), attr, None)
            else:
                attr_type = getattr(type(self._to_path_object(self._obj.values[0])), attr, None)

            # if we're asking for a property, do the calculation and return the result
            if isinstance(attr_type, property):

                def _to_apply(x):
                    res = getattr(self._to_path_object(x), attr)
                    return res if not isinstance(res, path_class) else str(res)

                return apply_series.apply(_to_apply)

            # if we're asking for a function, return a callable method
            elif isinstance(attr_type, (FunctionType, MethodType, LambdaType)):

                def _callable(*args, **kwargs):
                    if len(args) == 1 and isinstance(
                        args[0], (list, tuple, np.ndarray, pd.Series, pd.Index)
                    ):
                        other = args[0]
                        return self._elementwise(other, attr)

                    else:

                        def _to_apply(x):
                            res = getattr(self._to_path_object(x), attr)(*args, **kwargs)
                            return res if not isinstance(res, path_class) else str(res)

                        return apply_series.apply(_to_apply)

                return _callable

            else:
                raise AttributeError(f"Can't find or handle path attribute {attr}.")

        def _elementwise(self, other, attr):
            if isinstance(other, PathAccessor):
                other = other._obj

            other_array = np.array(other)

            if other_array.ndim > 1:
                raise ValueError(
                    "Can only do an elementwise operations with a 1d array, list, or Series."
                )

            if other_array.shape[0] != len(self._obj):
                raise ValueError(
                    "Can only do an elementwise operation with arrays of the same length."
                )

            def _to_apply(this_elem, other_elem):
                res = getattr(self._to_path_object(this_elem), attr)(other_elem)
                return res if not isinstance(res, path_class) else str(res)

            elementwise_result = pd.Series(
                [
                    _to_apply(this_elem, other_elem)
                    for this_elem, other_elem in zip(self._obj.values, other_array)
                ],
                index=self._obj.index,
            )

            return elementwise_result

        def _path_join(self, other, side):
            if isinstance(other, (list, tuple, np.ndarray, pd.Series, pd.Index, PathAccessor)):
                return self._elementwise(other, side)
            else:
                return self.__getattr__(side)(other)

        # operators don't override correctly unless defined
        def __truediv__(self, other):
            return self._path_join(other, "__truediv__")

        def __rtruediv__(self, other):
            return self._path_join(other, "__rtruediv__")

    return PathAccessor


def register_path_accessor(accessor_name, path_class, *args, **kwargs):
    accessor_class = path_accessor_factory(path_class, *args, **kwargs)

    # set name and docstring dynamically for reference
    accessor_class.__name__ = path_class.__name__ + "Accessor"
    accessor_class.__doc__ = accessor_class._doc_str_f.format(
        path_class=path_class.__name__, accessor_name=accessor_name
    )

    pd.api.extensions.register_series_accessor(accessor_name)(accessor_class)
    pd.api.extensions.register_index_accessor(accessor_name)(accessor_class)
