from pathlib import Path
from importlib.metadata import version
import hashlib,json,zipfile
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
KEEP_LOGS={'experiment.log','reference.log','intent.log','mas.log','tutorial_tests.log','assignment_tests.log','notebooks.log','slide_baseline.log','reports.log','report_summary.json','validation.json','document_generation.log'}

def include(p):
    rel=p.relative_to(ROOT)
    if any(part in {'.venv','__pycache__','.ipynb_checkpoints'} for part in rel.parts):return False
    if p.name in {'.DS_Store','artifact_manifest.json'} or p.suffix in {'.pyc','.zip'}:return False
    if rel.parts[0]=='build':return p.name in KEEP_LOGS or p.name.endswith('_CT_04_hainn.log')
    return True

def run():
    versions={x:version(x) for x in ['numpy','matplotlib','torch','nbformat','ipython','nbconvert','pypdf']}
    (ROOT/'environment_versions.json').write_text(json.dumps(versions,indent=2))
    manifest={'completed_date':'2026-10-28','timezone':'Asia/Ho_Chi_Minh','student':'Nguyễn Nam Hải — B23DCCN277',
              'pdfs':[],'files':[]}
    for p in sorted(ROOT.glob('*.pdf')):manifest['pdfs'].append({'file':p.name,'pages':len(PdfReader(p).pages)})
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and include(p))
    for p in files:manifest['files'].append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    mp=ROOT/'artifact_manifest.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    dest=ROOT.parent/'agent02_CT_04_hainn_full.zip'
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in files+[mp]:z.write(p,'solution/'+str(p.relative_to(ROOT)))
    with zipfile.ZipFile(dest) as z:assert z.testzip() is None
    print(json.dumps({'zip':str(dest),'bytes':dest.stat().st_size,'files':len(files)+1,'pdfs':manifest['pdfs']},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
