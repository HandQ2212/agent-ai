"""Rebuild the single Agent02 report from its chapters and real tutorial outputs."""
from pathlib import Path
import ast,subprocess,shutil,json
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent
CHAPTERS=['tutorial','tutorial_code_tong_hop','tutorial_results',
          'paper_intro','paper_mas','paper_rl','paper_technical','paper_synthesis',
          'assignment','assignment_results']
SOURCES=['slide_baseline.py','mas_system.py','train_intent.py','thuc_hanh_tong_hop.py','evaluate_mas.py','test_tutorial.py']

def build():
    code=ROOT/'report/code_ascii';code.mkdir(exist_ok=True)
    for name in SOURCES:
        original=(ROOT/'tutorial'/name).read_text(encoding='utf-8')
        def convert(c):
            v=ord(c)
            return c if v<128 else (r'\u%04x'%v if v<=65535 else r'\U%08x'%v)
        ascii_copy=''.join(map(convert,original))
        if ast.dump(ast.parse(original))!=ast.dump(ast.parse(ascii_copy)):
            raise ValueError('Printed code does not match original: '+name)
        (code/name).write_text(ascii_copy,encoding='ascii')
    cover=(ROOT/'report/cover_template.tex').read_text()
    cover=cover.replace('BÁO CÁO VỀ TÌM HIỂU AGENT','BÁO CÁO TỔNG HỢP AGENT 02')
    cover=cover.replace('{\\Large\\textbf{DISCOVERING AI AGENT}}',r'{\large\textbf{HỆ ĐA TÁC TỬ, REINFORCEMENT LEARNING\\[0.2cm] TUTORIAL -- PAPER -- ASSIGNMENT}}')
    (ROOT/'report/combined_cover.tex').write_text(cover)
    tutorial=(ROOT/'tutorial_CT_04_hainn.tex').read_text()
    preamble=tutorial.split('\\hypersetup{pdftitle=')[0]
    front=tutorial.split('\\pagenumbering{roman}',1)[1].split('\\input{report/chapters/tutorial.tex}',1)[0]
    front='\\pagenumbering{roman}'+front.replace('Ngày hoàn thiện: 28/10/2026.', 'Bản tổng hợp cập nhật ngày 29/10/2026.')
    pieces=[preamble,r'\hypersetup{pdftitle={BÁO CÁO TỔNG HỢP AGENT 02},pdfauthor={Nguyễn Nam Hải -- B23DCCN277}}',
            r'\begin{document}',r'\input{report/combined_cover.tex}',front,
            r'\part{TUTORIAL: PHÁT TRIỂN HỆ ĐA TÁC TỬ}',
            r'\input{report/chapters/tutorial.tex}',
            r'\input{report/chapters/tutorial_code_tong_hop.tex}',
            r'\input{report/chapters/tutorial_results.tex}',
            r'\clearpage',r'\part{ĐỌC VÀ PHÂN TÍCH HAI PAPER}',
            r'\input{report/chapters/paper_intro.tex}',r'\clearpage',
            r'\input{report/chapters/paper_mas.tex}',r'\clearpage',
            r'\input{report/chapters/paper_rl.tex}',r'\clearpage',
            r'\input{report/chapters/paper_technical.tex}',r'\clearpage',
            r'\input{report/chapters/paper_synthesis.tex}',
            r'\clearpage',r'\part{ASSIGNMENT: RL VÀ RULE-BASED AGENTS}',
            r'\input{report/chapters/assignment.tex}',
            r'\input{report/chapters/assignment_results.tex}',
            r'\input{report/references.tex}',r'\end{document}']
    tex=ROOT/'agent02_tong_hop.tex';tex.write_text('\n'.join(pieces)+'\n')
    builddir=ROOT/'build';builddir.mkdir(exist_ok=True)
    for run in range(1,4):
        r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',tex.name],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
        (builddir/f'combined_pass{run}.log').write_text(r.stdout)
        if r.returncode:raise RuntimeError(f'LaTeX compilation failed; see build/combined_pass{run}.log')
    log=(builddir/'agent02_tong_hop.log').read_text(errors='replace')
    if 'undefined references' in log or 'undefined on input' in log:raise RuntimeError('Unresolved cross references')
    target=OUT/'agent02_CT_04_hainn.pdf'
    shutil.copy2(builddir/'agent02_tong_hop.pdf',target)
    doc=PdfReader(target)
    text='\n'.join(p.extract_text() or '' for p in doc.pages)
    for required in ['TUTORIAL', 'PAPER', 'ASSIGNMENT', 'Nguyễn Nam Hải','B23DCCN277', 'thuc_hanh_tong_hop.py', 'Câu 10']:
        if required not in text:raise ValueError('Missing required content: '+required)
    details={'pdf':str(target),'pages':len(doc.pages),'bytes':target.stat().st_size,
             'tutorial_sources':[{'name':name,'lines':len((ROOT/'tutorial'/name).read_text().splitlines())} for name in SOURCES],
             'tutorial_tests':17,'assignment_tests':12}
    (builddir/'combined_report_summary.json').write_text(json.dumps(details,ensure_ascii=False,indent=2))
    print(json.dumps(details,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
