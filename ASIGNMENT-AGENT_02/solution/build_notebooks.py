from pathlib import Path
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
import os
from nbconvert import HTMLExporter
ROOT=Path(__file__).resolve().parent

def md(s):return nbf.v4.new_markdown_cell(s)
def code(s):return nbf.v4.new_code_cell(s)
setup='''from pathlib import Path
import sys, json, csv, inspect, subprocess
import numpy as np
from IPython.display import display, Image, HTML
ROOT = Path.cwd()
if not (ROOT / 'tutorial').exists():
    ROOT = ROOT.parent
assert (ROOT / 'tutorial/mas_system.py').exists(), 'Open notebook from solution/'
sys.path[:0] = [str(ROOT / 'tutorial'), str(ROOT / 'assignment')]

def show_csv(path, limit=30):
    rows = list(csv.DictReader(path.open(encoding='utf-8')))
    import html
    if not rows: return
    columns = list(rows[0])
    head = '<tr>' + ''.join('<th>'+html.escape(c)+'</th>' for c in columns) + '</tr>'
    body = ''.join('<tr>'+''.join('<td>'+html.escape(str(r[c]))+'</td>' for c in columns)+'</tr>' for r in rows[:limit])
    display(HTML('<table>'+head+body+'</table>'))
    print(f'{path.name}: {len(rows)} rows; showing {min(limit,len(rows))}')
print('Working directory:', ROOT)
'''
t=[md('''# Tutorial nâng cao: MAS với Python và PyTorch

Nguyễn Nam Hải — B23DCCN277 — CT/04/hainn.

Notebook chạy trực tiếp ví dụ shopping, failure injection, classifier đã train, thống kê và kiểm thử. Toàn bộ 20 unit và năm exercise được giải thích trong PDF tutorial. Các bảng đọc từ kết quả thực thi đầy đủ đã lưu; các cell có công tắc RETRAIN/RERUN mặc định False để tránh âm thầm ghi đè artifact khi chỉ xem.

**Dữ liệu tổng hợp.** Không có API/LLM hoặc giao dịch thật. Chọn Restart Kernel and Run All để kiểm lại các cell dưới đây.'''),code(setup),
md('## 1. PEAS và trách nhiệm\nCatalog truy hồi; recommender xếp hạng; policy kiểm budget/provenance; inventory kiểm kho; coordinator áp deadline và kiểm envelope. Hành động hệ là trả danh sách/trạng thái, không mua hàng.'),
code("from mas_system import *\nfor p in PRODUCTS:\n    print(p)\nprint('Stock:', STOCK)"),
md('## 2. Hợp đồng message\nSai task ID hoặc receiver không được dùng làm kết quả của yêu cầu hiện tại.'),
code("print(inspect.getsource(Message))\nprint(inspect.getsource(PolicyAgent))"),
md('## 3. Chạy luồng bình thường\nHai sản phẩm hợp lệ có ID p2 và p4. Laptop vượt budget; query trống không khớp toàn bộ.'),
code("system = Coordinator()\nresult = await system.shop('portable', 100, task_id='notebook-normal')\nprint(json.dumps(result, indent=2))\nassert [p['id'] for p in result['items']] == ['p2', 'p4']\ndisplay(HTML('<pre>'+json.dumps(system.trace, indent=2)+'</pre>'))"),
md('## 4. Budget, out of stock và đầu vào sai'),
code("for query,budget in [('portable',30),('sports',100),('',100),('unknown',100),('portable',-1),('portable',float('nan'))]:\n    print(query,budget,await system.shop(query,budget))"),
md('## 5. Bốn lỗi bắt buộc và một output giả\nTimeout dùng wait_for thật; dữ liệu kho cũ trả availability_unverified. Forged ID bị chặn trước khi kết luận availability.'),
code("for scenario in ['timeout','malformed','stale','forged']:\n    print(scenario,await system.shop('portable',100,scenario,task_id='notebook-'+scenario))"),
md('## 6. Ablation: bỏ kiểm chứng\nQuan sát sự khác biệt giữa nhiều thành viên và validation có hiệu lực.'),
code("unsafe = Coordinator(validate=False)\nfor scenario in ['stale','forged']:\n    print(scenario,await unsafe.shop('portable',100,scenario))"),
md('## 7. Baseline đơn có cùng điều kiện đúng\nCác đường bình thường cần tương đương. Baseline timeout được tiêm đồng bộ, không dùng để so trực tiếp thời gian chờ deadline với MAS.'),
code("for q in ['portable','study','sports','unknown','']:\n    for b in [0,30,100,1000]:\n        assert single_pipeline(q,b) == await system.shop(q,b)\nprint('20 normal input combinations matched')"),
md('## 8. Dữ liệu intent và chia theo nhóm\n432 câu tổng hợp; vocabulary chỉ xây trên train. Đối tượng được chia sẻ giữa split, nên bài test vẫn dễ hơn ngôn ngữ thật.'),
code("from train_intent import dataset, Router, run as train_intent\nrows=dataset()\nfrom collections import Counter\nprint(Counter(r['split'] for r in rows))\nfor split in ['train','validation','test']:\n    print(split,next(r for r in rows if r['split']==split))\nRETRAIN=False\nif RETRAIN:\n    train_intent(ROOT/'results/tutorial')\nelse:\n    print('Reading the supplied trained checkpoint and measured artifacts')"),
md('## 9. Kiến trúc và huấn luyện\nLoss nhận logits. Validation dùng chọn epoch và threshold; test giữ cho báo cáo cuối.'),
code("from train_intent import IntentNet\nprint(inspect.getsource(IntentNet))\nmetrics=json.loads((ROOT/'results/tutorial/intent_metrics.json').read_text())\nprint(json.dumps(metrics,ensure_ascii=False,indent=2))"),
code("display(Image(filename=str(ROOT/'results/tutorial/intent_training.png')))"),
md('## 10. Định tuyến và abstention\nĐộ tự tin cao không bảo đảm thuộc miền. Giữ nguyên các lỗi OOD để nhìn giới hạn.'),
code("router=Router(ROOT/'results/tutorial')\nfor text in ['tìm mua laptop cho tôi','gợi ý tham quan bảo tàng','hướng dẫn đặt hẹn giấy tờ bảo hiểm','xin chào','thời tiết hôm nay thế nào','giải phương trình']:\n    print(text,'->',router.route(text))"),
md('## 11. Benchmark B0–B3\n11 ca × 20 repetition mỗi kiến trúc. Success kiểm cả status và ID. B2 dùng câu shopping cố định để đo overhead, không đo routing đa miền.'),
code("show_csv(ROOT/'results/tutorial/mas_benchmark.csv')\nRERUN_BENCHMARK=False\nif RERUN_BENCHMARK:\n    from evaluate_mas import run as benchmark\n    await benchmark(ROOT/'results/tutorial')"),
md('## 12. Chạy bộ kiểm thử thực tế'),
code("completed=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tutorial'),'-p','test_*.py'],cwd=ROOT,capture_output=True,text=True)\nprint(completed.stdout+completed.stderr)\nassert completed.returncode==0"),
md('## 13. Kết luận thực hành\nB0/B1 cùng thành công trên bộ ca toy; MAS có thêm overhead. Validation có ích trong các ca lỗi. Classifier train thật đạt 100% test tổng hợp nhưng có OOD false acceptance. Năm exercise có đủ PEAS, code, model, failure injection, benchmark và demo; xem PDF để đọc toàn bộ giải thích và giới hạn.')]
a=[md('''# AGENT02 — Q-learning so với rule-based

Notebook kiểm mô hình, cập nhật Q, policy đóng băng, oracle và dữ liệu thí nghiệm A–E. Kết quả đầy đủ từ 36 lượt training của bản mở rộng đã được chạy bằng script và lưu trong results/assignment. Notebook mặc định **đọc các artifact này và thực thi những phép kiểm minh họa**, không chạy lại ngầm 3.6 triệu bước.

Bật RUN_FULL_EXPERIMENT=True nếu muốn train lại toàn bộ; thao tác đó ghi lại thư mục kết quả và nên chạy lại build_documents.py sau cùng. Báo cáo PDF trả lời đầy đủ 10 câu hỏi.'''),code(setup),
md('## 1. Cấu hình và môi trường'),
code("from agent02_experiment import *\nfrom dataclasses import asdict, replace\nprint(json.dumps(asdict(Config()),indent=2))\nenv=Environment(seed=42)\nprint('Initial:',env.reset())\nprint('Joint step:',env.step([0,1]))"),
md('## 2. Margin và bảng kỳ vọng\nBảng này là phép tính lý thuyết, khác với sampled reward.'),
code("cfg=Config()\nfor d in [0,1]:\n    for b in [0,1]:\n        print('demand=',d,'opponent=',b,'no discount=',expected_profit(cfg,d,0,b),'discount=',expected_profit(cfg,d,1,b))\nprint('Margins:',cfg.price-cfg.cost,cfg.price*(1-cfg.discount)-cfg.cost)"),
md('## 3. Q-learning update tính tay\nNonterminal cho kết quả 4.65; terminal không bootstrap.'),
code("agent=QLearningAgent()\nagent.q[0,0,0]=4;agent.q[1,1]=[5,2]\nagent.learn((0,0),0,6,(1,1))\nprint('Updated Q=',agent.q[0,0,0])\nassert np.isclose(agent.q[0,0,0],4.65)\nprint(inspect.getsource(QLearningAgent.learn))"),
md('## 4. Chạy training ngắn để kiểm tái lập\n200 episode chỉ là smoke demonstration, không thay thế 5.000 episode của bảng kết quả chính.'),
code("small=replace(cfg,episodes=200)\nagent,_,history,counts=train(small,42)\nprint('Episodes:',len(history),'training action counts:',counts.tolist())\nprint('First:',history[0]);print('Last:',history[-1])\nq=agent.q.copy();measured,_=evaluate(cfg,agent.q,seed=500042)\nassert np.array_equal(q,agent.q)\nprint('Frozen smoke evaluation:',measured)"),
md('## 5. Đọc kết quả baseline 42 đã train đủ'),
code("summary=json.loads((ROOT/'results/assignment/summary.json').read_text())\nprint('Environment:',summary['python'],summary['numpy'])\nprint('Q:',np.array(summary['baseline']['q']))\nshow_csv(ROOT/'results/assignment/baseline_42_summary.csv')"),
md('## 6. Đối chiếu code gốc\nSeed giống số học nhưng stream khác. Cả hai kết quả được lưu riêng.'),
code("show_csv(ROOT/'results/assignment/reference_original_42_summary.csv')"),
md('## 7. Alpha và epsilon trên năm seed'),
code("show_csv(ROOT/'results/assignment/aggregate.csv')\nshow_csv(ROOT/'results/assignment/configurations.csv')"),
code("display(Image(filename=str(ROOT/'results/assignment/learning_curve.png')))\ndisplay(Image(filename=str(ROOT/'results/assignment/learning_rates.png')))\ndisplay(Image(filename=str(ROOT/'results/assignment/exploration.png')))"),
md('## 8. So sánh công bằng\nMọi focal policy cùng fixed rule opponent, cùng demand và uniform sales tape.'),
code("show_csv(ROOT/'results/assignment/fair_comparison.csv')\ndisplay(Image(filename=str(ROOT/'results/assignment/evaluation.png')))"),
md('## 9. Chứng minh thiếu state bằng hai lịch sử\nCùng observation (high, opponent previous 0), nhưng own previous action khác làm opponent current action khác.'),
code("for own_previous in [0,1]:\n    opponent_current=1*own_previous\n    print('own_previous=',own_previous,'observed=(1,0)','opponent_current=',opponent_current,'profit_no_discount=',expected_profit(cfg,1,0,opponent_current))"),
md('## 10. DP hữu hạn chân trời với đầy đủ state'),
code("policy,values=exact_best_response(cfg)\nprint('Policy shape:',policy.shape,'all choose no discount:',bool((policy==0).all()))\nassert (policy==0).all()\ndp_result,_=evaluate(cfg,policy,seed=800011)\nprint(dp_result)\nprint(inspect.getsource(exact_best_response))"),
md('## 11. Exact policy evaluation bằng occupancy\nPhép tính không lấy mẫu, tách khác biệt policy khỏi noise evaluation.'),
code("from analyze_exact import exact_mean\nexact,steps=exact_mean(cfg,np.array(summary['baseline']['q']))\nprint('Baseline42 exact mean:',exact)\nshow_csv(ROOT/'results/assignment/exact_policy_values.csv')"),
md('## 12. Robustness discount 40% và self-play'),
code("show_csv(ROOT/'results/assignment/robustness_discount40.csv')\nshow_csv(ROOT/'results/assignment/selfplay_summary.csv')"),
md('## 13. Kiểm thử và tùy chọn chạy lại đầy đủ'),
code("completed=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'assignment'),'-p','test_*.py'],cwd=ROOT,capture_output=True,text=True)\nprint(completed.stdout+completed.stderr)\nassert completed.returncode==0\nRUN_FULL_EXPERIMENT=False\nif RUN_FULL_EXPERIMENT:\n    run(ROOT/'results/assignment',episodes=5000)\nelse:\n    print('Full experiment already measured; flag False preserves supplied artifacts')"),
md('## 14. Kết luận\nBaseline RL chưa vượt rule/DP trong mô hình này. Một run có thể rất khác nhóm seed; ảnh hưởng state thiếu và target terminal cần được phân tích. Reward training không đồng nhất frozen performance. Dữ liệu mô phỏng không tạo bằng chứng lợi ích kinh doanh ngoài thực tế.')]
for filename,cells in [('tutorial_CT_04_hainn',t),('agent02_CT_04_hainn',a)]:
    nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}})
    p=ROOT/(filename+'.ipynb');nbf.write(nb,p)
    # Execute real code in-process; sandbox blocks Jupyter's local TCP ports.
    os.chdir(ROOT)
    InteractiveShell.clear_instance()
    shell=InteractiveShell.instance()
    count=0
    for cell in nb.cells:
        if cell.cell_type!='code': continue
        count+=1
        with capture_output(stdout=True,stderr=True,display=True) as captured:
            result=shell.run_cell(cell.source,store_history=True)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError(str(result.error_before_exec or result.error_in_exec)+'\n'+captured.stdout+'\n'+captured.stderr)
        cell.execution_count=count;cell.outputs=[]
        if captured.stdout: cell.outputs.append(nbf.v4.new_output('stream',name='stdout',text=captured.stdout))
        if captured.stderr: cell.outputs.append(nbf.v4.new_output('stream',name='stderr',text=captured.stderr))
        for rich in captured.outputs:
            cell.outputs.append(nbf.v4.new_output('display_data',data=rich.data,metadata=rich.metadata))
    nb.metadata['execution_method']='Real execution via IPython in-process; no mock output. Local Jupyter sockets unavailable in sandbox.' 
    nbf.write(nb,p)
    exporter=HTMLExporter();exporter.exclude_input_prompt=False;exporter.exclude_output_prompt=False
    body,_=exporter.from_notebook_node(nb);(ROOT/(filename+'_notebook.html')).write_text(body)
    print(filename, 'executed',sum(c.cell_type=='code' for c in nb.cells),'code cells',flush=True)
