"""Offline configuration boundary tests. No database or network is used."""
import importlib.util
import os
from pathlib import Path
import ssl
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))


def valid_values():
    return dict(
        DB2_LOCATION_NAME="TESTLOC", DB2_DATABASE="TESTLOC", DB2_HOSTNAME="db2.example.invalid",
        DB2_PORT="448", DB2_USERNAME="test_user", DB2_PASSWORD="private-test-secret",
        DB2_SSL_CONNECTION="true", DB2_SSL_SERVER_CERTIFICATE="certs/db2-ca.cer",
        DB2_READ_ONLY_ACCOUNT_CONFIRMED="true", DB2_ALLOWED_SCHEMAS="APP",
        DB2_ALLOWED_TABLES="APP.ITEMS,APP.OTHER", DB2_MAX_ROWS="100",
        DB2_MAX_BYTES="65536", DB2_QUERY_TIMEOUT_SECONDS="10",
        DB2_CONNECT_TIMEOUT_SECONDS="5", DB2_MAX_OFFSET="10000",
    )


def write_env(root, values):
    (root / '.env').write_text('\n'.join(k + "='" + v.replace("'", "\\'") + "'" for k, v in values.items()), encoding='utf-8')


def fixture(root):
    (root / 'certs').mkdir()
    cert = (Path(__file__).parent/'fixtures/test-only-ca.pem').read_text(encoding='ascii')
    (root / 'certs/db2-ca.cer').write_text(cert)
    write_env(root, valid_values())


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('config'), 'config.py must implement the fail-closed .env contract')
        import config
        self.mod = config
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        fixture(self.root)

    def load(self, **changes):
        vals = valid_values()
        vals.update(changes)
        write_env(self.root, vals)
        return self.mod.load_config(self.root)

    def test_valid_settings_and_password_never_in_repr(self):
        cfg = self.load()
        self.assertEqual(cfg.location_name, 'TESTLOC')
        self.assertEqual(cfg.certificate, (self.root / 'certs/db2-ca.cer').resolve())
        self.assertNotIn('private-test-secret', repr(cfg))
        self.assertEqual(cfg.allowed_tables, frozenset({('APP', 'ITEMS'), ('APP', 'OTHER')}))

    def test_environment_cannot_override_or_supply_missing_secrets(self):
        with patch.dict(os.environ, {'DB2_PASSWORD':'ambient-secret', 'DB2_HOSTNAME':'bad.invalid'}):
            self.assertEqual(self.load().password, 'private-test-secret')
            vals = valid_values(); del vals['DB2_PASSWORD']; write_env(self.root, vals)
            with self.assertRaises(self.mod.ConfigError): self.mod.load_config(self.root)

    def test_dotenv_interpolation_disabled_and_quoted_hash_preserved(self):
        self.assertEqual(self.load(DB2_PASSWORD='${HOME}#;$literal').password, '${HOME}#;$literal')

    def test_missing_or_insecure_fields_rejected_without_value_leak(self):
        bad = {
            'DB2_LOCATION_NAME':['', 'a;b', 'PHYSICAL\nINJECT'],
            'DB2_DATABASE':['', 'DIFFERENT'],
            'DB2_HOSTNAME':['', 'a;SECURITY=NONE', 'https://db2.invalid', 'a/b', 'bad\n'],
            'DB2_PORT':['0','65536','-1','443;PWD=x','443.0'],
            'DB2_SSL_CONNECTION':['','false','1'],
            'DB2_READ_ONLY_ACCOUNT_CONFIRMED':['','false'],
            'DB2_USERNAME':['','x\n'], 'DB2_PASSWORD':['','x\x00'],
            'DB2_MAX_ROWS':['0','501','True'], 'DB2_MAX_BYTES':['1','1048577'],
            'DB2_QUERY_TIMEOUT_SECONDS':['0','61'], 'DB2_CONNECT_TIMEOUT_SECONDS':['0','31'],
            'DB2_MAX_OFFSET':['-1','100001'],
            'DB2_ALLOWED_SCHEMAS':['APP,*','APP;DROP','app'],
            'DB2_ALLOWED_TABLES':['APP.*','OTHER.ITEMS','APP.ITEMS;DROP','APP.ITEMS.X'],
        }
        for key, vals in bad.items():
            for value in vals:
                with self.subTest(key=key,value=value):
                    with self.assertRaises(self.mod.ConfigError) as e: self.load(**{key:value})
                    self.assertNotIn('private-test-secret', str(e.exception))
                    self.assertNotIn('a;SECURITY=NONE', str(e.exception))

    def test_empty_allowlists_deny_all_without_broadening(self):
        cfg = self.load(DB2_ALLOWED_SCHEMAS='', DB2_ALLOWED_TABLES='')
        self.assertEqual(cfg.allowed_schemas, frozenset())
        self.assertEqual(cfg.allowed_tables, frozenset())

    def test_certificate_missing_invalid_and_path_escape_rejected(self):
        for value in ['../outside.cer', '/tmp/outside.cer', 'certs/../outside.cer', 'certs/other.cer']:
            with self.subTest(value=value), self.assertRaises(self.mod.ConfigError):
                self.load(DB2_SSL_SERVER_CERTIFICATE=value)
        (self.root/'certs/db2-ca.cer').write_text('not a certificate')
        with self.assertRaises(self.mod.ConfigError): self.load()
        (self.root/'certs/db2-ca.cer').unlink()
        with self.assertRaises(self.mod.ConfigError): self.load()

    def test_der_certificate_is_parsed_without_network(self):
        path=self.root/'certs/db2-ca.cer'
        path.write_bytes(ssl.PEM_cert_to_DER_cert(path.read_text()))
        self.assertEqual(self.mod.load_config(self.root).certificate,path.resolve())

    def test_env_and_certificate_symlinks_rejected(self):
        original = self.root / '.env'; renamed = self.root / 'other.env'
        original.rename(renamed); original.symlink_to(renamed)
        with self.assertRaises(self.mod.ConfigError): self.mod.load_config(self.root)
        original.unlink(); renamed.rename(original)
        cert = self.root/'certs/db2-ca.cer'; target = self.root/'cert.cer'
        cert.rename(target); cert.symlink_to(target)
        with self.assertRaises(self.mod.ConfigError): self.mod.load_config(self.root)

    def test_duplicate_malformed_unknown_db2_settings_fail_closed(self):
        for suffix in ['\nDB2_PORT=449', '\nDB2_BYPASS_TLS=true', '\nDB2_PASSWORD="unterminated']:
            write_env(self.root, valid_values())
            with (self.root/'.env').open('a') as f: f.write(suffix)
            with self.assertRaises(self.mod.ConfigError): self.mod.load_config(self.root)

if __name__ == '__main__': unittest.main()

class PortableFixtureTests(unittest.TestCase):
    def test_fixture_does_not_depend_on_machine_trust_store(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as tmp, patch.object(ssl,'get_default_verify_paths',return_value=SimpleNamespace(cafile=None)):
            fixture(Path(tmp))
            self.assertTrue((Path(tmp)/'certs/db2-ca.cer').is_file())
