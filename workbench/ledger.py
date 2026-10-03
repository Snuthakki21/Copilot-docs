"""One serialized ledger writer, versioned events and an atomic one-packet quota."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import threading
from .domain import ValidationError, identity, encode, require


def now(): return datetime.now(timezone.utc).isoformat()


class Ledger:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        state = self.root / '.migration'
        require(not state.is_symlink(), 'Unsafe ledger path')
        state.mkdir(exist_ok=True)
        self.lock = threading.RLock()
        require(not (state/'ledger.sqlite').is_symlink(), 'Unsafe ledger database path')
        self.db = sqlite3.connect(state/'ledger.sqlite', check_same_thread=False, timeout=10)
        try:
            self.db.row_factory = sqlite3.Row
            self.db.execute('PRAGMA foreign_keys=ON')
            # Rollback journaling avoids WAL-reset bugs and filesystem assumptions.
            self.db.execute('PRAGMA journal_mode=DELETE')
            self.db.executescript(Path(__file__).with_name('schema.sql').read_text())
        except Exception:
            self.db.close();raise

    def create(self, manifest, demo=False):
        pid = identity(manifest['id'])
        doc = {**manifest, 'demo': bool(demo), 'analysis': None, 'artifacts': [], 'blockers': [], 'runs': [], 'answers': None, 'revision': 1}
        with self.lock, self.db:
            try:
                self.db.execute('INSERT INTO processes(id,name,status,demo,document,created,updated) VALUES(?,?,?,?,?,?,?)', (pid, manifest['name'], 'READY', int(demo), encode(doc).decode(), now(), now()))
            except sqlite3.IntegrityError as exc: raise ValidationError('Process already exists; select it or use a new process ID') from exc
        return self.get(pid)

    def get(self, pid):
        identity(pid)
        with self.lock: row = self.db.execute('SELECT * FROM processes WHERE id=?', (pid,)).fetchone()
        require(row is not None, 'Process not found')
        doc = json.loads(row['document'])
        return {**doc, 'status': row['status'], 'packet_issued': bool(row['packet_issued']), 'packet_imported': bool(row['packet_imported']), 'packet_hash': row['packet_hash'], 'created': row['created'], 'updated': row['updated']}

    def list(self, include_demo=False):
        with self.lock: rows = self.db.execute('SELECT id FROM processes WHERE demo=0 OR ?=1 ORDER BY created', (int(include_demo),)).fetchall()
        return [self.get(r['id']) for r in rows]

    def controls(self, pid):
        """Read durable operator controls without materializing synthetic results.

        SQLite's JSON projection keeps per-record cancellation checks small.
        Older SQLite builds without JSON support retain the safe full-read path.
        """
        identity(pid)
        with self.lock:
            try:
                row=self.db.execute("SELECT status, json_extract(document,'$.control_revision') AS control_revision, json_extract(document,'$.cancel_requested') AS cancel_requested, json_extract(document,'$.resume_status') AS resume_status FROM processes WHERE id=?",(pid,)).fetchone()
            except sqlite3.OperationalError as exc:
                if 'no such function: json_extract' not in str(exc):raise
                return self.get(pid)
        require(row is not None,'Process not found')
        result={key:row[key] for key in row.keys() if row[key] is not None}
        result['blockers']=[{'kind':'cancelled','message':'Operator cancelled this process'}] if result.get('cancel_requested') else []
        return result

    def save(self, doc, status=None):
        pid = identity(doc['id'])
        canonical = {k:v for k,v in doc.items() if k not in {'status','packet_issued','packet_imported','packet_hash','created','updated'}}
        with self.lock, self.db:
            require(self.db.execute('SELECT 1 FROM processes WHERE id=?', (pid,)).fetchone(), 'Process not found')
            self.db.execute('UPDATE processes SET document=?,status=COALESCE(?,status),updated=? WHERE id=?', (encode(canonical).decode(), status, now(), pid))
        return self.get(pid)

    def event(self, pid, stage, message, payload=None):
        with self.lock, self.db:
            self.db.execute('INSERT INTO events(process_id,stage,message,payload,created) VALUES(?,?,?,?,?)', (pid,stage,message,encode(payload or {}).decode(),now()))

    def events(self, pid, after=0):
        with self.lock: rows = self.db.execute('SELECT * FROM events WHERE process_id=? AND seq>? ORDER BY seq LIMIT 2000', (pid,after)).fetchall()
        return [{**dict(r),'payload':json.loads(r['payload'])} for r in rows]

    def issue_packet(self, pid, fingerprint):
        with self.lock, self.db:
            cur = self.db.execute('UPDATE processes SET packet_issued=1,packet_hash=? WHERE id=? AND packet_issued=0', (fingerprint,pid))
            require(cur.rowcount == 1, 'This process has already issued its one SME questionnaire')

    def consume_return(self, pid, answers):
        with self.lock, self.db:
            doc = self.get(pid)
            require(doc['packet_issued'] and not doc['packet_imported'], 'SME return already consumed or packet not issued')
            doc['answers'] = answers
            canonical = {k:v for k,v in doc.items() if k not in {'status','packet_issued','packet_imported','packet_hash','created','updated'}}
            cur = self.db.execute('UPDATE processes SET packet_imported=1,document=?,status=?,updated=? WHERE id=? AND packet_imported=0', (encode(canonical).decode(),'QUEUED_VERIFY',now(),pid))
            require(cur.rowcount == 1, 'SME return already consumed')

    def register_assets(self, pid, assets):
        with self.lock, self.db:
            for asset in assets:
                self.db.execute('INSERT OR IGNORE INTO assets VALUES(?,?,?,?,?)',(asset['id'],asset['kind'],asset['name'],asset['source_hash'],encode(asset).decode()))
                self.db.execute('INSERT OR IGNORE INTO process_assets VALUES(?,?)',(pid,asset['id']))

    def assets(self, pid=None, include_demo=False):
        with self.lock:
            if pid: rows = self.db.execute('SELECT a.document FROM assets a JOIN process_assets p ON a.id=p.asset_id WHERE p.process_id=?',(pid,)).fetchall()
            else: rows = self.db.execute('SELECT DISTINCT a.document FROM assets a JOIN process_assets p ON a.id=p.asset_id JOIN processes x ON x.id=p.process_id WHERE x.demo=0 OR ?=1',(int(include_demo),)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def snapshot(self, pid, document):
        canonical=encode(document).decode()
        with self.lock, self.db:
            existing=self.db.execute('SELECT 1 FROM snapshots WHERE process_id=? AND document=?',(pid,canonical)).fetchone()
            if not existing:self.db.execute('INSERT INTO snapshots(process_id,document,created) VALUES(?,?,?)',(pid,canonical,now()))

    def complete_report(self, doc, metrics):
        """Commit accepted history, report certification and terminal event together."""
        pid=identity(doc['id'])
        canonical={k:v for k,v in doc.items() if k not in {'status','packet_issued','packet_imported','packet_hash','created','updated'}}
        metric_text=encode(metrics).decode()
        status='COMPLETED_WITH_BLOCKERS' if doc['blockers'] else 'COMPLETED'
        with self.lock, self.db:
            require(self.db.execute('SELECT 1 FROM processes WHERE id=?',(pid,)).fetchone(),'Process not found')
            if not self.db.execute('SELECT 1 FROM snapshots WHERE process_id=? AND document=?',(pid,metric_text)).fetchone():
                self.db.execute('INSERT INTO snapshots(process_id,document,created) VALUES(?,?,?)',(pid,metric_text,now()))
            self.db.execute('UPDATE processes SET document=?,status=?,updated=? WHERE id=?',(encode(canonical).decode(),status,now(),pid))
            self.db.execute('INSERT INTO events(process_id,stage,message,payload,created) VALUES(?,?,?,?,?)',(pid,'complete','Report inspection passed; technical completion recorded for the stated source-derived POC boundary',encode({}).decode(),now()))
        return self.get(pid)

    def history(self, pid=None):
        with self.lock: rows = self.db.execute('SELECT * FROM snapshots WHERE process_id=? OR ? IS NULL ORDER BY seq',(pid,pid)).fetchall()
        return [{**dict(r),'document':json.loads(r['document'])} for r in rows]

    def close(self):
        with self.lock: self.db.close()
