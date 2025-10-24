import json
from pathlib import Path
from threading import Lock

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

_locks = {}

def _get_lock(path: Path):
    key = str(path)
    if key not in _locks:
        _locks[key] = Lock()
    return _locks[key]


def read_json(filename: str, default=None):
    path = DATA_DIR / filename
    if not path.exists():
        return default if default is not None else []
    with _get_lock(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default if default is not None else []


def write_json(filename: str, data):
    path = DATA_DIR / filename
    with _get_lock(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class JsonStore:
    """Simple JSON-backed store for a single file."""
    def __init__(self, filepath: str):
        # allow either a full path or a filename relative to data dir
        p = Path(filepath)
        if p.is_absolute():
            self.path = p
        else:
            self.path = DATA_DIR / filepath

    def _read(self):
        if not self.path.exists():
            return []
        with _get_lock(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []

    def _write(self, data):
        with _get_lock(self.path):
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self):
        return self._read()

    def get_by_id(self, id):
        items = self._read()
        return next((i for i in items if i.get('id') == id), None)

    def add(self, item):
        items = self._read()
        items.append(item)
        self._write(items)

    def update(self, id, new_item):
        items = self._read()
        for idx, it in enumerate(items):
            if it.get('id') == id:
                items[idx] = new_item
                self._write(items)
                return True
        return False

    def delete(self, id):
        items = self._read()
        new_items = [i for i in items if i.get('id') != id]
        self._write(new_items)
        return True
