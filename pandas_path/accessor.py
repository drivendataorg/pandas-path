from pathlib import Path

import pandas as pd


@pd.api.extensions.register_series_accessor("path")
@pd.api.extensions.register_index_accessor("path")
class PathAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj
        
    @staticmethod
    def _validate(obj):
        [Path(x) for x in obj.values]

    def __getattr__(self, attr):
        apply_series = self._obj.to_series() if isinstance(self._obj, pd.Index) else self._obj
        
        # check the type of this attribute on a Path object
        attr_type = getattr(type(Path()), attr, None)

        # if we're asking for a property, do the calculation and return the result
        if isinstance(attr_type, property):
            return apply_series.apply(lambda x: getattr(Path(x), attr))

        # if we're asking for a function, return a callable method
        elif isinstance(attr_type, (FunctionType, MethodType, LambdaType)):
            def _callable(*args, **kwargs):
                return apply_series.apply(lambda x: getattr(Path(x), attr)(*args, **kwargs))

            return _callable
            
        else:
            raise AttributeError(f"Can't find or handle path attribute {attr}.")
            
    # operators don't override correctly unless defined
    def __truediv__(self, other):
        return self.__getattr__("__truediv__")(other)
    
    def __rtruediv__(self, other):
        return self.__getattr__("__rtruediv__")(other)