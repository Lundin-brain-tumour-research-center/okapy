import contextlib
from shutil import rmtree
from tempfile import mkdtemp
import json
import numpy as np

@contextlib.contextmanager
def make_temp_directory():
    temp_dir = mkdtemp()
    try:
        yield temp_dir
    finally:
        rmtree(temp_dir)


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NpEncoder, self).default(obj)
