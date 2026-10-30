"""Package the single consolidated PDF and the reproducible supplementary code."""
from pathlib import Path
import hashlib,json,zipfile
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent

def allowed(path):
    rel=path.relative_to(ROOT)
    if any(x in {'.venv','__pycache__','.ipynb_checkpoints'} for x in rel.parts):return False
    if path.suffix in {'.pdf','.pyc','.zip'} or path.name=='.DS_Store':return False
    if rel.parts[0]=='build':return path.name in {'tutorial_thuc_hanh_output.txt','tutorial_thuc_hanh_tests.txt','assignment_tong_hop_tests.txt','combined_report_summary.json'}
    if rel.parts[0] in {'assets','report','results','assignment','tutorial'}:return True
    return path.name in {'README_TONG_HOP.md','requirements.txt','build_combined_report.py','package_combined_report.py',
      'tutorial_CT_04_hainn.tex','agent02_tong_hop.tex','tutorial_CT_04_hainn.ipynb','tutorial_CT_04_hainn_notebook.html',
      'agent02_CT_04_hainn.ipynb','agent02_CT_04_hainn_notebook.html','environment_versions.json'}

def run():
    pdf=PARENT/'agent02_CT_04_hainn.pdf';files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and allowed(p)]
    records=[{'path':'agent02_CT_04_hainn.pdf','sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'size':pdf.stat().st_size}]
    for p in files:records.append({'path':'solution/'+str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size})
    manifest={'pdf_pages':len(PdfReader(pdf).pages),'files':records}
    dest=PARENT/'agent02_tong_hop_code.zip'
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        z.write(pdf,'agent02_CT_04_hainn.pdf')
        for p in files:z.write(p,'solution/'+str(p.relative_to(ROOT)))
        z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.lower().endswith('.pdf')])==1
    print(json.dumps({'zip':str(dest),'bytes':dest.stat().st_size,'files':len(records)+1,'pdf_pages':manifest['pdf_pages']},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
