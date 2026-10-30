"""Compile the 3 standalone reports; existing TeX fragments do not require Pandoc."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,shutil,json
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
STEMS=['tutorial_CT_04_hainn','paper_CT_04_hainn','agent02_CT_04_hainn']
def compile_one(stem):
    (ROOT/'build').mkdir(exist_ok=True)
    for i in range(3):
        r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',stem+'.tex'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
        (ROOT/'build'/f'{stem}_pass{i+1}.txt').write_text(r.stdout)
        if r.returncode:raise RuntimeError(f'LaTeX failed: {stem}, pass {i+1}; see build/{stem}_pass{i+1}.txt')
    log=(ROOT/'build'/(stem+'.log')).read_text(errors='replace')
    if 'undefined references' in log or 'Citation ' in log and 'undefined' in log:raise RuntimeError('Unresolved references in '+stem)
    shutil.copy2(ROOT/'build'/(stem+'.pdf'),ROOT/(stem+'.pdf'))
    return {'file':stem+'.pdf','pages':len(PdfReader(ROOT/(stem+'.pdf')).pages),'bytes':(ROOT/(stem+'.pdf')).stat().st_size}
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:result=list(pool.map(compile_one,STEMS))
    (ROOT/'build/report_summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
