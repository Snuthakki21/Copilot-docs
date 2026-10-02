"""Local .env-only settings and conservative Db2 identifier validation."""
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
import re
import ssl

from dotenv import dotenv_values
from dotenv.parser import parse_stream

IDENTIFIER = re.compile(r'[A-Z][A-Z0-9_@$#]{0,127}\Z')
HOSTNAME = re.compile(r'(?=.{1,253}\Z)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*\Z')
FIELDS = frozenset('LOCATION_NAME DATABASE HOSTNAME PORT USERNAME PASSWORD SSL_CONNECTION SSL_SERVER_CERTIFICATE READ_ONLY_ACCOUNT_CONFIRMED ALLOWED_SCHEMAS ALLOWED_TABLES MAX_ROWS MAX_BYTES QUERY_TIMEOUT_SECONDS CONNECT_TIMEOUT_SECONDS MAX_OFFSET'.split())


class ConfigError(ValueError):
    """Messages are static and never include supplied configuration values."""


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError('Expected an uppercase regular Db2 identifier.')
    return value


@dataclass(frozen=True)
class Config:
    project_root: Path
    location_name: str
    database: str
    hostname: str
    port: int
    username: str = field(repr=False)
    password: str = field(repr=False)
    certificate: Path
    allowed_schemas: frozenset
    allowed_tables: frozenset
    max_rows: int
    max_bytes: int
    query_timeout: int
    connect_timeout: int
    max_offset: int


def load_config(project_root):
    """Never discover parent .env files, interpolate secrets, or read os.environ."""
    try:
        root = Path(project_root).resolve(strict=True)
        env_file = root / '.env'
        if env_file.is_symlink() or not env_file.is_file() or env_file.stat().st_size > 65536:
            raise ConfigError('Create a regular project-root .env file from the template.')
        text = env_file.read_text(encoding='utf-8')
        seen = set()
        for item in parse_stream(StringIO(text)):
            if item.error or (item.key is not None and item.key in seen):
                raise ConfigError('Malformed or duplicate .env setting.')
            if item.key:
                seen.add(item.key)
                if item.key.startswith('DB2_') and item.key[4:] not in FIELDS:
                    raise ConfigError('Unknown DB2 setting in .env.')
        values = dotenv_values(stream=StringIO(text), interpolate=False)

        def required(name):
            value = values.get('DB2_' + name)
            if not isinstance(value, str) or not value or any(ord(c) < 32 or ord(c) == 127 for c in value):
                raise ConfigError('Missing or invalid DB2_' + name + ' in .env.')
            return value

        def number(name, default, low, high):
            value = values.get('DB2_' + name, str(default))
            if not isinstance(value, str) or not re.fullmatch(r'[0-9]+', value):
                raise ConfigError('Invalid DB2_' + name + ' in .env.')
            n = int(value)
            if not low <= n <= high:
                raise ConfigError('Out-of-range DB2_' + name + ' in .env.')
            return n

        location = identifier(required('LOCATION_NAME'))
        if len(location) > 16:
            raise ConfigError('Invalid DB2_LOCATION_NAME in .env.')
        database = identifier(required('DATABASE'))
        if database != location:
            raise ConfigError('DB2_DATABASE must equal the DBA-confirmed DRDA location name.')
        host = required('HOSTNAME')
        if not HOSTNAME.fullmatch(host):
            raise ConfigError('Invalid DB2_HOSTNAME in .env.')
        if required('SSL_CONNECTION') != 'true':
            raise ConfigError('DB2_SSL_CONNECTION must be true; TLS cannot be disabled.')
        if required('READ_ONLY_ACCOUNT_CONFIRMED') != 'true':
            raise ConfigError('A DBA-confirmed SELECT-only account is required.')
        relative_cert = required('SSL_SERVER_CERTIFICATE')
        if relative_cert != 'certs/db2-ca.cer':
            raise ConfigError('Certificate must be certs/db2-ca.cer inside this project.')
        cert = root / relative_cert
        if (root/'certs').is_symlink() or cert.is_symlink() or not cert.is_file() or cert.stat().st_size > 1048576:
            raise ConfigError('A regular project certificate file is required.')
        cert = cert.resolve(strict=True)
        if not cert.is_relative_to(root) or any(c in str(cert) for c in ';{}\n\r\x00'):
            raise ConfigError('Certificate path cannot safely be used by the IBM driver.')
        certificate_data = cert.read_bytes()
        if b'PRIVATE KEY' in certificate_data:
            raise ConfigError('Use a public CA/server certificate, never a private key.')
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cadata=(certificate_data.decode('ascii') if b'-----BEGIN CERTIFICATE-----' in certificate_data else certificate_data))
        schemas_text = values.get('DB2_ALLOWED_SCHEMAS', '')
        tables_text = values.get('DB2_ALLOWED_TABLES', '')
        if not isinstance(schemas_text, str) or not isinstance(tables_text, str):
            raise ConfigError('Invalid allowlist settings.')
        schemas = frozenset(identifier(x.strip()) for x in schemas_text.split(',')) if schemas_text else frozenset()
        tables = set()
        for entry in tables_text.split(',') if tables_text else []:
            parts = entry.strip().split('.')
            if len(parts) != 2:
                raise ConfigError('Each allowed table must be SCHEMA.TABLE.')
            schema, table = map(identifier, parts)
            if schema not in schemas:
                raise ConfigError('Every allowed table schema must be explicitly allowed.')
            tables.add((schema, table))
        if len(schemas) > 64 or len(tables) > 200:
            raise ConfigError('Allowlist exceeds the supported bounded size.')
        return Config(root, location, database, host, number('PORT', 0, 1, 65535),
                      required('USERNAME'), required('PASSWORD'), cert, schemas, frozenset(tables),
                      number('MAX_ROWS', 100, 1, 500), number('MAX_BYTES', 65536, 2048, 1048576),
                      number('QUERY_TIMEOUT_SECONDS', 15, 1, 60), number('CONNECT_TIMEOUT_SECONDS', 10, 1, 30),
                      number('MAX_OFFSET', 10000, 0, 100000))
    except ConfigError:
        raise
    except Exception:
        raise ConfigError('Invalid local Db2 configuration or certificate.') from None
