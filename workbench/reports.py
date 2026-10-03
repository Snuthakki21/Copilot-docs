"""One frozen metric model drives CSV, workbook and editable PowerPoint."""
import csv
from pathlib import Path
from io import StringIO
from openpyxl import Workbook
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from .domain import encode, atomic_json, sha, require
from .ledger import now

def metrics(ledger, doc):
    a=doc.get('analysis') or {'programs':{},'assets':[],'rules':[]}
    assets=a['assets'];run=doc['runs'][-1] if doc['runs'] else {'programs':{}}
    verified=0;matches=0;cases=0
    answers=(doc.get('answers') or {}).get('items',{})
    for name,p in a['programs'].items():
        r=run['programs'].get(name)
        if not r:continue
        cases+=len(r['actual']);matches+=len(r['actual'])-len(r['differences'])
        if not r['differences'] and r['coverage']['complete'] and not p['blockers']:
            verified+=sum(answers.get(rule['id'],{}).get('answer')=='Yes' and not answers.get(rule['id'],{}).get('correction') for rule in p['rules'])
    versions=doc.get('program_versions',{})
    target_loc=sum(sum(bool(x.strip()) and not x.lstrip().startswith('#') for x in (ledger.root/'shared/target/python'/f'{v}.py').read_text().splitlines()) for v in set(versions.values()))
    return {'process_id':doc['id'],'demo':doc['demo'],'source_programs':len(a['programs']),
        'source_copybooks':sum(x['kind']=='copybook' for x in assets),
        'source_bms_screens':sum(len(x.get('screens',[])) for x in assets),'source_cics_transactions':None,
        'source_db2_table_references':len({t.upper() for x in assets for t in x.get('tables',[])}),
        'source_vsam_files':None,'inbound_interfaces':None,'outbound_interfaces':None,
        'target_python_programs':len(versions),'target_react_business_screens':0,'target_business_rest_apis':0,
        'source_code_loc':sum(x['loc']['code'] for x in assets),'source_physical_loc':sum(x['loc']['physical'] for x in assets),
        'target_program_code_loc':target_loc,'rules_documented':len(a['rules']),'rules_verified':verified,
        'known_rule_verification_percent':round(100*verified/len(a['rules']),2) if a['rules'] else None,
        'synthetic_cases':cases,'matching_cases':matches,'unresolved_blockers':len(doc['blockers']),
        'unsupported_source_lines':sum(x['disposition']=='unsupported' for p in a['programs'].values() for x in p['coverage']),
        'observed_mainframe_parity':False,'evidence_basis':'SOURCE_DERIVED_EXPECTED',
        'verification_percent_denominator':'Extracted known rules only; unsupported and unknown rules are not silently excluded from completion gates.',
        'target_environment':'Non-production Python / SQLite; JSON record adapter'}

def portfolio(ledger):
    assets=ledger.assets();p=ledger.list()
    return {'processes':len(p),'unique_program_versions':sum(x['kind']=='cobol_program' for x in assets),
        'unique_copybook_versions':sum(x['kind']=='copybook' for x in assets),
        'program_memberships':sum(len((x.get('analysis') or {}).get('programs',{})) for x in p),
        'completed_processes':sum(x['status']=='COMPLETED' for x in p),'demo_excluded':True}

def generate_reports(ledger,doc,root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    m=metrics(ledger,doc);model={'created':now(),'metrics':m,'portfolio':portfolio(ledger),'blockers':doc['blockers'],'lineage':(doc.get('analysis') or {}).get('graph',[])}
    atomic_json(root/'metrics.json',model)
    csvout=StringIO();writer=csv.writer(csvout);writer.writerow(['Metric','Value'])
    for k,v in m.items():writer.writerow([k,'Unknown' if v is None else v])
    (root/'metrics.csv').write_text(csvout.getvalue())
    book=Workbook();sheet=book.active;sheet.title='Metrics';sheet.append(['Metric','Value'])
    for k,v in m.items():sheet.append([k,'Unknown' if v is None else v])
    sheet.column_dimensions['A'].width=48;sheet.column_dimensions['B'].width=90;sheet.freeze_panes='B2'
    history=book.create_sheet('History');history.append(['Process','Created','Programs','Verified rules'])
    for h in ledger.history():
        if h['document'].get('demo'):continue
        history.append([h['process_id'],h['created'],h['document']['source_programs'],h['document']['rules_verified']])
    book.save(root/'metrics.xlsx');book.close()
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    def slide(title,rows,note):
        s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor(248,250,252)
        box=s.shapes.add_textbox(Inches(.6),Inches(.35),Inches(12.1),Inches(.7))
        p=box.text_frame.paragraphs[0];p.text=title;p.font.size=Pt(27);p.font.bold=True;p.font.color.rgb=RGBColor(15,35,60)
        table=s.shapes.add_table(len(rows)+1,2,Inches(.65),Inches(1.4),Inches(12),Inches(min(4.5,(len(rows)+1)*.52))).table
        table.columns[0].width=Inches(7.6);table.columns[1].width=Inches(4.4)
        for i,row in enumerate([['Measure','Evidence / value']]+rows):
            for j,value in enumerate(row):
                cell=table.cell(i,j);cell.text=str(value);cell.fill.solid();cell.fill.fore_color.rgb=RGBColor(15,35,60) if i==0 else RGBColor(255,255,255)
                for par in cell.text_frame.paragraphs:
                    par.font.size=Pt(16);par.font.color.rgb=RGBColor(255,255,255) if i==0 else RGBColor(25,45,65)
        b=s.shapes.add_textbox(Inches(.65),Inches(6.35),Inches(12),Inches(.8));b.text_frame.word_wrap=True
        b.text_frame.text=note
        for par in b.text_frame.paragraphs:par.font.size=Pt(13);par.font.color.rgb=RGBColor(70,85,105)
    slide('Modernization POC · '+doc['id'],[['Source COBOL programs',m['source_programs']],['Copybooks',m['source_copybooks']],['Generated Python programs',m['target_python_programs']],['Synthetic cases / matching',f"{m['synthetic_cases']} / {m['matching_cases']}"],['Unresolved blockers',m['unresolved_blockers']]],'Fictional demonstration' if doc['demo'] else 'Evidence is source-derived; no mainframe program was executed.')
    slide('Before → after',[['BMS screens → React business screens',f"{m['source_bms_screens']} → 0"],['Business REST APIs generated',0],['COBOL + copybook code LOC → program Python LOC',f"{m['source_code_loc']} → {m['target_program_code_loc']}"],['CICS / VSAM / inbound / outbound counts','Unknown until evidenced'],['Target environment','Python / SQLite (non-production)']],'Workbench UI and its control endpoints are excluded from modernized business-screen/API counts. LOC is a size metric, not a parity metric.')
    slide('Rule verification',[['Extracted known rules',m['rules_documented']],['SME-confirmed + tested rules',m['rules_verified']],['Known-rule verification',str(m['known_rule_verification_percent'])+'%'],['Unsupported source lines',m['unsupported_source_lines']],['Observed mainframe parity','NOT established']],'The percentage covers extracted known rules only. Unknown/unsupported behavior remains a blocker; passing synthetic tests is not proof of full legacy parity.')
    pf=model['portfolio']
    slide('Portfolio progress',[['Production processes',pf['processes']],['Unique source program versions',pf['unique_program_versions']],['Program memberships across processes',pf['program_memberships']],['Unique copybook versions',pf['unique_copybook_versions']],['Completed without blockers',pf['completed_processes']]],'Demonstrations are excluded. Assets are deduplicated by program identity and source hash; membership counts preserve reuse.')
    slide('Evidence and decisions',[['Source snapshot',(doc.get('analysis') or {}).get('source_snapshot','Unavailable')[:20]],['SME review','One packet / one return per process'],['Expected vs actual','Frozen source IR vs executed Python'],['Open decisions',m['unresolved_blockers']],['Completion','WITH BLOCKERS' if doc['blockers'] else 'Supported POC boundary verified']],'See metrics.json, source-analysis.json and each synthetic run for complete hashes, source spans, cases, actual results, differences and unresolved answers.')
    prs.save(root/'management.pptx')
    inspected=Presentation(root/'management.pptx');require(len(inspected.slides)==5,'Deck incomplete')
    for s in inspected.slides:
        for shape in s.shapes:require(shape.left>=0 and shape.top>=0 and shape.left+shape.width<=inspected.slide_width and shape.top+shape.height<=inspected.slide_height,'Deck geometry exceeds canvas')
    require(str(m['source_programs']) in '\n'.join(c.text for s in inspected.slides for sh in s.shapes if sh.has_table for row in sh.table.rows for c in row.cells),'Deck metric missing')
    paths=[root/f for f in ['metrics.json','metrics.csv','metrics.xlsx','management.pptx']]
    atomic_json(root/'inspection.json',{'verified':True,'checks':['5 editable slides','all shapes within canvas','source program metric present'],'powerpoint_render_checked':False,'sha256':{p.name:sha(p.read_bytes()) for p in paths}})
    ledger.snapshot(doc['id'],m)
    return paths+[root/'inspection.json']
