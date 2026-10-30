"""Artifact audit; does not retrain models or overwrite measured results."""
from pathlib import Path
import csv,json,re
import nbformat
import numpy as np
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent

def run():
    report={'pdfs':[],'notebooks':[],'checks':[]}
    for stem in ['tutorial_CT_04_hainn','paper_CT_04_hainn','agent02_CT_04_hainn']:
        p=ROOT/(stem+'.pdf');r=PdfReader(p);txt='\n'.join(page.extract_text()or'' for page in r.pages)
        assert not r.is_encrypted and len(r.pages)>15
        assert 'Nguyễn Nam Hải' in txt and 'B23DCCN277' in txt
        assert '??' not in txt,'Unresolved citation/reference'
        if stem.startswith('agent02'):
            for i in range(1,11):assert re.search(r'Câu\s+'+str(i)+r'\b',txt),f'Missing question {i}'
        if stem.startswith('tutorial'):
            for i in range(1,21):assert re.search(r'Unit\s+'+str(i)+r'\b',txt),f'Missing unit {i}'
        report['pdfs'].append({'file':p.name,'pages':len(r.pages),'text_characters':len(txt)})
        log=(ROOT/'build'/(stem+'.log')).read_text(errors='replace')
        assert 'undefined references' not in log and 'undefined on input' not in log
        report['checks'].append(f'{stem}: readable, identified, complete headings, resolved references')
    for stem,count in [('tutorial_CT_04_hainn',14),('agent02_CT_04_hainn',15)]:
        nb=nbformat.read(ROOT/(stem+'.ipynb'),as_version=4);cells=[c for c in nb.cells if c.cell_type=='code']
        assert len(cells)==count and all(c.execution_count for c in cells)
        assert not any(o.output_type=='error' for c in cells for o in c.outputs)
        assert all(c.outputs for c in cells)
        assert any(o.output_type=='display_data' and 'image/png' in o.data for c in cells for o in c.outputs), 'Missing rendered images'
        assert any(o.output_type=='display_data' and 'text/html' in o.data for c in cells for o in c.outputs), 'Missing HTML tables'
        assert (ROOT/(stem+'_notebook.html')).stat().st_size>50000
        report['notebooks'].append({'file':stem+'.ipynb','executed_code_cells':len(cells),'output_blocks':sum(len(c.outputs) for c in cells)})
    def rows(name,folder='assignment'):
        return list(csv.DictReader((ROOT/'results'/folder/name).open()))
    conf=rows('configurations.csv');assert len(conf)==25
    assert {int(r['seed']) for r in conf}=={11,22,33,44,55}
    for file in (ROOT/'results/assignment').glob('*_training.csv'):
        assert len(list(csv.DictReader(file.open())))==5000,file.name
    assert len(rows('fair_comparison.csv'))==25
    assert len(rows('robustness_discount40.csv'))==20
    assert len(rows('selfplay_summary.csv'))==10
    exact=rows('exact_policy_values.csv');assert len(exact)==25
    assert max(abs(float(r['sample_error'])) for r in exact)<1
    for label in {r['configuration'] for r in conf}:
        v=[float(r['mean_reward']) for r in conf if r['configuration']==label]
        agg=next(r for r in rows('aggregate.csv') if r['configuration']==label)
        assert np.isclose(np.mean(v),float(agg['mean'])) and np.isclose(np.std(v,ddof=1),float(agg['sd']))
    assert len(rows('intent_dataset.csv','tutorial'))==432
    assert len(rows('intent_test_predictions.csv','tutorial'))==108
    assert len(rows('mas_benchmark_raw.csv','tutorial'))==880
    assert json.loads((ROOT/'results/tutorial/slide_baseline.json').read_text())['checks_passed']==5
    for f,n in [('tutorial_tests.log',17),('assignment_tests.log',12)]:
        text=(ROOT/'build'/f).read_text();assert 'OK' in text and f'Ran {n} tests' in text
    report['checks']+=['Raw CSV row counts match protocol','Aggregates match measured per-seed data','Exact policy values consistent with sampled evaluation','Original slide baseline: 5 checks passed','17 tutorial and 12 assignment tests passed']
    (ROOT/'build/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2));return report
if __name__=='__main__':run()
