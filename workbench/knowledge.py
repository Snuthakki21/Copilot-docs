"""Compact, provenance-bound approved knowledge; user Markdown is evidence only."""
from .domain import sha, encode, atomic_json
from .ledger import now


def update_knowledge(ledger, process):
    answers=(process.get('answers') or {}).get('items',{})
    with ledger.lock,ledger.db:
        for rule in process['analysis']['rules']:
            answer=answers.get(rule['id'],{})
            if answer.get('answer')!='Yes' or answer.get('correction'):continue
            key=sha(process['analysis']['source_snapshot']+rule['id'])
            doc={'id':key,'rule_id':rule['id'],'statement':rule['plain'],'applicability':{'source_snapshot':process['analysis']['source_snapshot'],'process_id':process['id']},'source_refs':rule['source_refs'],'reviewer':answer['reviewer'],'packet_hash':process['packet_hash'],'confidence':'SME confirmed interpretation; target verification is separate','supersedes':[]}
            ledger.db.execute('INSERT OR REPLACE INTO knowledge VALUES(?,?,?)',(key,encode(doc).decode(),now()))
        rows=ledger.db.execute('SELECT document FROM knowledge ORDER BY id').fetchall()
    import json
    records=[json.loads(r[0]) for r in rows]
    atomic_json(ledger.root/'knowledge'/'records.json',records)
    index='# SME-confirmed knowledge index\n\n'+str(len(records))+' provenance-bound interpretations; target verification is separate. Canonical structured records: records.json.\n\n'+'\n'.join('- '+r['rule_id']+': '+r['statement'] for r in records)
    (ledger.root/'knowledge'/'INDEX.md').write_text(index,encoding='utf-8')
    return len(records)
