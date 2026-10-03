"""Validated identities, bounded documents and immutable evidence writes."""
import hashlib
import json
import math
from pathlib import Path
import re
import uuid
import zipfile
from io import BytesIO

MAX_UPLOAD = 8 * 1024 * 1024
ID = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]{0,79}$')
DEVICES = {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition: raise ValidationError(message)


def identity(value):
    require(isinstance(value, str) and ID.fullmatch(value), 'Use an ID beginning with a letter and containing letters, numbers, hyphens or underscores.')
    require(value.upper() not in DEVICES,'Use a portable ID; Windows device names are reserved')
    return value


def safe_path(root, relative):
    root = Path(root).resolve()
    require(isinstance(relative, str) and relative and '\\' not in relative and ':' not in relative, 'Invalid relative path')
    require(not any(ord(c)<32 or c in '<>"|?*' for c in relative),'Path contains unsupported control or platform-reserved characters')
    rel = Path(relative)
    require(not rel.is_absolute() and '..' not in rel.parts, 'Path must remain inside its process directory')
    require(all(not p.endswith(('.', ' ')) and p.split('.')[0].upper() not in DEVICES for p in rel.parts),'Path uses a reserved or ambiguous platform filename')
    candidate = root / rel
    require(not any(p.is_symlink() for p in [candidate, *candidate.parents] if p != root.parent), 'Symlink paths are not accepted')
    require(candidate.resolve().is_relative_to(root), 'Path escapes its directory')
    return candidate


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def decode(data, limit=MAX_UPLOAD):
    require(len(data) <= limit, 'Document exceeds the configured size limit')
    def pairs(entries):
        result = {}
        for k, v in entries:
            require(k not in result, 'Duplicate JSON key')
            result[k] = v
        return result
    def floating(v):
        n = float(v)
        require(math.isfinite(n), 'Nonfinite numbers are not accepted')
        return n
    try:
        return json.loads(data, object_pairs_hook=pairs, parse_float=floating, parse_constant=lambda v: require(False, 'Invalid JSON number'))
    except (ValueError, TypeError, RecursionError) as exc:
        raise ValidationError('Invalid JSON document') from exc


def write_new(path, data):
    path = Path(path)
    require(not path.exists() and not path.is_symlink(), 'Evidence already exists; create a new version')
    require(not any(p.is_symlink() for p in path.parents), 'Symlink output parents are not accepted')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as out: out.write(data)
    return sha(data)


def atomic_json(path, value):
    path = Path(path)
    require(not path.is_symlink() and not any(p.is_symlink() for p in path.parents), 'Unsafe state path')
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.parent / ('.' + path.name + '.' + uuid.uuid4().hex)
    temp.write_bytes(encode(value))
    temp.replace(path)


def checked_zip(data):
    require(len(data) <= MAX_UPLOAD, 'Archive exceeds upload limit')
    try:
        archive = zipfile.ZipFile(BytesIO(data))
        entries = archive.infolist()
        require(len(entries) <= 300 and sum(x.file_size for x in entries) <= 32 * 1024 * 1024, 'Archive expansion exceeds limit')
        for x in entries:
            require(not x.filename.startswith(('/', '\\')) and '..' not in Path(x.filename).parts and '\\' not in x.filename, 'Unsafe archive path')
            require(x.file_size <= 8 * 1024 * 1024, 'Archive member exceeds limit')
            if x.filename.endswith('.xml'):
                body = archive.read(x).upper()
                require(b'<!DOCTYPE' not in body and b'<!ENTITY' not in body, 'XML declarations/entities are not accepted')
        return archive
    except (zipfile.BadZipFile, OSError) as exc:
        raise ValidationError('Invalid ZIP/XLSX document') from exc
