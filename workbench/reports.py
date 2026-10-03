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
from .coverage import build_coverage, write_coverage

def metrics(ledger, doc, coverage=None, portfolio_model=None):
    coverage=coverage or build_coverage(doc,ledger.root)
    summary=coverage['summary']
    final_status='COMPLETED' if summary['completion_eligible'] and not doc.get('blockers') and not doc.get('cancel_requested') else 'COMPLETED_WITH_BLOCKERS'
    projected=portfolio_model if portfolio_model is not None else report_portfolio(ledger,doc,final_status)
    a=doc.get('analysis') or {'programs':{},'assets':[],'rules':[]}
    assets=[x for x in a['assets'] if x.get('selected',True)];run=doc['runs'][-1] if doc['runs'] else {'programs':{}}
    verified=0;matches=0;cases=0
    answers=(doc.get('answers') or {}).get('items',{})
    for name,p in a['programs'].items():
        r=run['programs'].get(name)
        if not r:continue
        cases+=len(r['actual'])
        program_rows=[row for row in coverage['rows'] if row['source_path']==p['path'] and row['disposition'] not in ('non_executable','out_of_scope')]
        if program_rows and all(row['disposition'] in ('mapped_verified','platform_replaced_verified') for row in program_rows) and not r['differences'] and r['coverage']['complete'] and not p['blockers']:
            matches+=len(r['actual'])-len(r['differences'])
            verified+=sum(answers.get(rule['id'],{}).get('answer')=='Yes' and not answers.get(rule['id'],{}).get('correction') for rule in p['rules'])
    versions=doc.get('program_versions',{})
    target_loc=sum(sum(bool(x.strip()) and not x.lstrip().startswith('#') for x in ((ledger.root/'shared/target/python'/f'{v}.py').read_text().splitlines() if (ledger.root/'shared/target/python'/f'{v}.py').is_file() else [])) for v in set(versions.values()))
    return {'process_id':doc['id'],'demo':doc['demo'],'report_final_status':final_status,
        'portfolio_completed_processes':projected['completed_processes'],
        'portfolio_basis':'Includes current report outcome upon atomic artifact acceptance; excludes demonstrations',
        'source_programs':len(a['programs']),
        'source_copybooks':sum(x['kind']=='copybook' for x in assets),
        'source_bms_screens':sum(len(x.get('screens',[])) for x in assets),'source_cics_transactions':None,
        'source_db2_table_references':len({t.upper() for x in assets for t in x.get('tables',[])}),
        'source_vsam_files':None,'inbound_interfaces':None,'outbound_interfaces':None,
        'target_python_programs':len(versions),'target_react_business_screens':0,'target_business_rest_apis':0,
        'source_code_loc':sum(x['loc']['code'] for x in assets),'source_physical_loc':sum(x['loc']['physical'] for x in assets),
        'target_program_code_loc':target_loc,'rules_documented':len(a['rules']),'rules_verified':verified,
        'known_rule_verification_percent':round(100*verified/len(a['rules']),2) if a['rules'] else None,
        'synthetic_cases':cases,'matching_cases':matches,'matching_cases_basis':'Matching cases credited only for intact, SME-confirmed whole-program evidence','unresolved_blockers':len(doc['blockers']),
        'unsupported_source_lines':sum(x['disposition']=='unsupported' for p in a['programs'].values() for x in p['coverage']),
        'source_inventory_files':summary['source_files'],'source_accounted_lines':summary['source_lines'],
        'source_in_scope_lines':summary['in_scope_lines'],'source_out_of_scope_lines':summary['out_of_scope_lines'],
        'source_applicable_lines':summary['applicable_lines'],'source_verified_applicable_lines':summary['verified_applicable_lines'],
        'source_applicable_line_verification_percent':summary['line_verification_percent'],
        'source_semantic_units':summary['semantic_units']['total'],'source_applicable_semantic_units':summary['semantic_units']['applicable'],
        'source_verified_semantic_units':summary['semantic_units']['verified'],
        'source_semantic_unit_verification_percent':summary['semantic_units']['verification_percent'],
        'source_blocked_lines':summary['dispositions']['blocked'],'source_non_executable_lines':summary['non_executable_lines'],
        'source_unverified_mapped_lines':summary['dispositions']['mapped_unverified']+summary['dispositions']['platform_replaced_unverified'],
        'source_platform_replaced_verified_lines':summary['dispositions']['platform_replaced_verified'],
        'source_full_accounting':summary['fully_accounted'],'source_completion_eligible':summary['completion_eligible'],
        'source_integrity_errors':len(summary['integrity_errors']),
        'observed_mainframe_parity':False,'evidence_basis':'SOURCE_DERIVED_EXPECTED',
        'verification_percent_denominator':'Extracted known rules only; unsupported and unknown rules are not silently excluded from completion gates.',
        'target_environment':'Non-production Python / SQLite; JSON record adapter'}

def portfolio(ledger):
    with ledger.lock:
        assets=ledger.assets();p=ledger.list()
    return {'processes':len(p),'unique_program_versions':sum(x['kind']=='cobol_program' for x in assets),
        'unique_copybook_versions':sum(x['kind']=='copybook' for x in assets),
        'program_memberships':sum(len((x.get('analysis') or {}).get('programs',{})) for x in p),
        'completed_processes':sum(x['status']=='COMPLETED' for x in p),'demo_excluded':True}

def report_portfolio(ledger,doc,final_status):
    """Project only this report's accepted outcome; keep live portfolio unchanged.

    The coordinator commits these frozen metrics with terminal status only after
    mandatory artifact inspection. Failed or interrupted output remains a
    projection and never adds accepted history or live completion credit.
    """
    with ledger.lock:
        result=portfolio(ledger)
        if not doc.get('demo'):
            current=next((p for p in ledger.list() if p['id']==doc['id']),None)
            if current:
                result['completed_processes']+=int(final_status=='COMPLETED')-int(current['status']=='COMPLETED')
    result['basis']='Includes current report outcome upon atomic artifact acceptance; excludes demonstrations'
    return result


def generate_reports(ledger,doc,root,checkpoint=None):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    coverage=build_coverage(doc,ledger.root,checkpoint=checkpoint)
    coverage_paths=write_coverage(coverage,root)
    final_status='COMPLETED' if coverage['summary']['completion_eligible'] and not doc.get('blockers') and not doc.get('cancel_requested') else 'COMPLETED_WITH_BLOCKERS'
    pf=report_portfolio(ledger,doc,final_status)
    m=metrics(ledger,doc,coverage,portfolio_model=pf);model={'created':now(),'metrics':m,'portfolio':pf,'blockers':doc['blockers'],'lineage':(doc.get('analysis') or {}).get('graph',[])}
    atomic_json(root/'metrics.json',model)
    csvout=StringIO();writer=csv.writer(csvout);writer.writerow(['Metric','Value'])
    for k,v in m.items():writer.writerow([k,'Unknown' if v is None else v])
    (root/'metrics.csv').write_text(csvout.getvalue())
    book=Workbook();sheet=book.active;sheet.title='Metrics';sheet.append(['Metric','Value'])
    for k,v in m.items():sheet.append([k,'Unknown' if v is None else v])
    sheet.column_dimensions['A'].width=48;sheet.column_dimensions['B'].width=90;sheet.freeze_panes='B2'
    portfolio_sheet=book.create_sheet('Portfolio');portfolio_sheet.append(['Measure','Value'])
    for key,value in model['portfolio'].items():portfolio_sheet.append([key,value])
    portfolio_sheet.column_dimensions['A'].width=42;portfolio_sheet.column_dimensions['B'].width=95
    history=book.create_sheet('History');history.append(['Process','Created','Programs','Verified rules','Acceptance'])
    accepted_history=ledger.history()
    for h in accepted_history:
        if h['document'].get('demo'):continue
        history.append([h['process_id'],h['created'],h['document']['source_programs'],h['document']['rules_verified'],'Accepted snapshot'])
    if not doc['demo'] and not any(h['process_id']==doc['id'] and encode(h['document'])==encode(m) for h in accepted_history):
        history.append([doc['id'],model['created'],m['source_programs'],m['rules_verified'],'Current report upon atomic acceptance'])
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
        b.text_frame.text=('Fictional test fixture. ' if doc.get('fixture_only') else '')+note
        for par in b.text_frame.paragraphs:par.font.size=Pt(13);par.font.color.rgb=RGBColor(70,85,105)
    slide('Modernization POC · '+doc['id'],[['Source COBOL programs',m['source_programs']],['Copybooks',m['source_copybooks']],['Generated Python programs',m['target_python_programs']],['Synthetic cases / matching',f"{m['synthetic_cases']} / {m['matching_cases']}"],['Unresolved blockers',m['unresolved_blockers']]],'Fictional demonstration' if doc['demo'] else 'Evidence is source-derived; no mainframe program was executed.')
    slide('Before → after',[['BMS screens → React business screens',f"{m['source_bms_screens']} → 0"],['Business REST APIs generated',0],['All selected source code LOC → program Python LOC',f"{m['source_code_loc']} → {m['target_program_code_loc']}"],['CICS / VSAM / inbound / outbound counts','Unknown until evidenced'],['Target environment','Python / SQLite (non-production)']],'Workbench UI and its control endpoints are excluded from modernized business-screen/API counts. LOC is a size metric, not a parity metric.')
    slide('Rule verification',[['Extracted known rules',m['rules_documented']],['SME-confirmed + tested rules',m['rules_verified']],['Known-rule verification',str(m['known_rule_verification_percent'])+'%'],['Unsupported source lines',m['unsupported_source_lines']],['Observed mainframe parity','NOT established']],'The percentage covers extracted known rules only. Unknown/unsupported behavior remains a blocker; passing synthetic tests is not proof of full legacy parity.')
    cs=coverage['summary']
    slide('Complete source accountability',[
        ['Frozen export files / physical lines',f"{cs['source_files']} / {cs['source_lines']}"],
        ['Applicable source lines: verified / total',f"{cs['verified_applicable_lines']} / {cs['applicable_lines']}"],
        ['Blocked / mapped but unverified lines',f"{m['source_blocked_lines']} / {m['source_unverified_mapped_lines']}"],
        ['Non-executable / explicitly out-of-scope lines',f"{cs['non_executable_lines']} / {cs['out_of_scope_lines']}"],
        ['Semantic units: verified / applicable',f"{cs['semantic_units']['verified']} / {cs['semantic_units']['applicable']}"],
        ['Verified platform replacement lines',m['source_platform_replaced_verified_lines']]],
        'coverage.json/CSV/XLSX/HTML preserve every original file and line with target spans, versions, tests and reasons. Line, semantic-unit and extracted-rule percentages use separate denominators.')
    pf=model['portfolio']
    slide('Portfolio progress',[['Production processes',pf['processes']],['Unique source program versions',pf['unique_program_versions']],['Program memberships across processes',pf['program_memberships']],['Unique copybook versions',pf['unique_copybook_versions']],['Completed without blockers',pf['completed_processes']]],'Includes the current process outcome upon atomic report acceptance; demonstrations are excluded. Assets deduplicate by identity and source hash; memberships preserve reuse.')
    slide('Evidence and decisions',[['Source snapshot',(doc.get('analysis') or {}).get('source_snapshot','Unavailable')[:20]],['SME review','One packet / one return per process'],['Expected vs actual','Frozen source IR vs executed Python'],['Open decisions',m['unresolved_blockers']],['Completion','WITH BLOCKERS' if m['report_final_status']=='COMPLETED_WITH_BLOCKERS' else 'Supported POC boundary verified']],'See metrics.json, source-analysis.json and each synthetic run for complete hashes, source spans, cases, actual results, differences and unresolved answers.')
    prs.save(root/'management.pptx')
    inspected=Presentation(root/'management.pptx');require(len(inspected.slides)==6,'Deck incomplete')
    for s in inspected.slides:
        for shape in s.shapes:require(shape.left>=0 and shape.top>=0 and shape.left+shape.width<=inspected.slide_width and shape.top+shape.height<=inspected.slide_height,'Deck geometry exceeds canvas')
    require(str(m['source_programs']) in '\n'.join(c.text for s in inspected.slides for sh in s.shapes if sh.has_table for row in sh.table.rows for c in row.cells),'Deck metric missing')
    paths=[root/f for f in ['metrics.json','metrics.csv','metrics.xlsx','management.pptx']]+coverage_paths
    atomic_json(root/'inspection.json',{'verified':True,'checks':['6 editable slides','full source accountability in JSON/CSV/XLSX/HTML','all shapes within canvas','source program metric present'],'powerpoint_render_checked':False,'sha256':{p.name:sha(p.read_bytes()) for p in paths}})
    return paths+[root/'inspection.json']
