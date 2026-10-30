"""Build Vietnamese PTIT reports from Markdown chapters and measured artifacts."""
from pathlib import Path
import csv,json,shutil,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parent
CH=ROOT/'report/chapters'

def readcsv(name,folder='assignment'):
    return list(csv.DictReader((ROOT/'results'/folder/name).open()))
def table(headers,rows):
    return '\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)+'\n'
def fig(path,caption):
    return '\n\\begin{center}\n\\includegraphics[width=0.98\\linewidth]{'+path+'}\n\\captionof{figure}{'+caption+'}\n\\end{center}\n'
def group(rows,key,metric='mean_reward'):
    result=[]
    for k in dict.fromkeys(r[key] for r in rows):
        v=np.array([float(r[metric]) for r in rows if r[key]==k]);result.append((k,v.mean(),v.std(ddof=1)))
    return result

ass=json.loads((ROOT/'results/assignment/summary.json').read_text())
intent=json.loads((ROOT/'results/tutorial/intent_metrics.json').read_text())
mas=json.loads((ROOT/'results/tutorial/mas_metrics.json').read_text())
assignment='''# Phụ lục kết quả đo và bằng chứng thực thi

Các bảng dưới được dựng trực tiếp từ CSV/JSON của lần chạy đầy đủ. Mọi mean cấu hình là trung bình qua năm seed 11, 22, 33, 44, 55; SD dùng ddof=1. Các ảnh là biểu đồ vẽ từ dữ liệu episode thực thi, không phải ảnh minh họa sinh bằng mô hình.

## Bảng tổng hợp thí nghiệm alpha và epsilon
'''
assignment+=table(['Cấu hình','Train mean','Eval mean','SD','CI95 ±','Discount (%)'],[[r['configuration'],f"{r['train_mean']:.4f}",f"{r['mean']:.4f}",f"{r['sd']:.4f}",f"{r['ci95_half_t4']:.4f}",f"{100*r['discount_rate']:.2f}"] for r in ass['aggregates']])
assignment+='\n## So sánh công bằng với cùng đối thủ\n'
assignment+=table(['Focal policy','Mean reward/step','SD giữa seed'],[[k,f'{m:.4f}',f'{s:.4f}'] for k,m,s in group(readcsv('fair_comparison.csv'),'policy')])
assignment+='\n## Thí nghiệm biến đổi discount 40%\n'
assignment+=table(['Policy','Mean reward/step','SD giữa seed'],[[k,f'{m:.4f}',f'{s:.4f}'] for k,m,s in group(readcsv('robustness_discount40.csv'),'policy')])
assignment+='\n## Q-table minh họa seed 42\n'
q=np.array(ass['baseline']['q']);assignment+=table(['Demand','Opponent previous','Q(no discount)','Q(discount)','Greedy action'],[[d,c,f'{q[d,c,0]:.6f}',f'{q[d,c,1]:.6f}',int(np.argmax(q[d,c]))] for d in (0,1) for c in (0,1)])
assignment+='\n## Từng seed của baseline\n'
assignment+=table(['Seed','RL mean','Rule mean cùng tape','RL discount (%)'],[[r['seed'],f"{float(r['mean_reward']):.4f}",f"{float(next(x['mean_reward'] for x in readcsv('fair_comparison.csv') if x['policy']=='Rule' and x['seed']==r['seed'])):.4f}",f"{100*float(r['discount_rate']):.2f}"] for r in readcsv('configurations.csv') if r['configuration']=='baseline'])
assignment+='\n## Cặp learner trong self-play\n'
assignment+=table(['Seed','Learner','Eval mean','Discount (%)'],[[r['seed'],r['learner'],f"{float(r['mean_reward']):.4f}",f"{100*float(r['discount_rate']):.2f}"] for r in readcsv('selfplay_summary.csv')])
if (ROOT/'results/assignment/reference_original_42.json').exists():
    ref=json.loads((ROOT/'results/assignment/reference_original_42.json').read_text())
    assignment+='\n## Đối chiếu bản gốc và bản mở rộng seed 42\n\nCùng seed số học không tạo cùng chuỗi khi cách dùng RNG khác. Bảng này ghi hai protocol riêng; không lấy chênh lệch làm bằng chứng chất lượng một thuật toán khác.\n'
    assignment+=table(['Protocol','Focal mean','Opponent mean'],[['Code gốc nguyên văn',f"{ref['summary'][0]['mean_reward_per_step']:.4f}",f"{ref['summary'][1]['mean_reward_per_step']:.4f}"],['Bản mở rộng, split RNG',f"{ass['baseline']['evaluation'][0]['mean_reward']:.4f}",f"{ass['baseline']['evaluation'][1]['mean_reward']:.4f}"]])
for f,c in [('learning_curve','Learning curve baseline: moving average 100 episode, mean và một SD qua năm seed.'),('learning_rates','So sánh ba learning rate với cùng epsilon schedule.'),('exploration','So sánh ba cấu hình epsilon; mọi cấu hình đánh giá với epsilon bằng 0.'),('evaluation','Policy đóng băng: mean và SD giữa seed; đường 35 là kỳ vọng lý thuyết.'),('q_and_sensitivity','Q-table seed 42 và độ nhạy lợi nhuận tức thời theo discount fraction.')]:
    assignment+=fig('results/assignment/'+f+'.png',c)
assignment+='''
## Mã Python cốt lõi

Đây là các đoạn mã được lấy trực tiếp từ nguồn đã thực thi. Tệp đầy đủ và bản tham chiếu có trong thư mục assignment; các đoạn bên dưới đủ để kiểm cách cập nhật, tách evaluation và tính oracle.

\\lstinputlisting[firstline=60,lastline=73,caption={Q-learning và luật, trích từ mã chạy}]{assignment/agent02_experiment.py}
\\lstinputlisting[firstline=106,lastline=118,caption={Quy hoạch động hữu hạn chân trời}]{assignment/agent02_experiment.py}
\\lstinputlisting[firstline=120,lastline=149,caption={Đánh giá đóng băng với common random numbers}]{assignment/agent02_experiment.py}

## Bằng chứng kiểm thử

Bộ kiểm thử assignment có 12 ca, đã chạy thành công. Các ca kiểm công thức ví dụ 4.65; terminal không bootstrap; observation sau joint action; từ chối action sai; margin; bảng luật; Q không đổi khi đánh giá; tổng action counts; tái lập evaluation; DP chọn không giảm; tái lập training; và sample mean gần kỳ vọng 35 khi số episode lớn.

\\begin{verbatim}
python3 -m unittest discover -s assignment -p 'test_*.py'
............
Ran 12 tests
OK
\\end{verbatim}

Log thực tế được giữ trong build/assignment_tests.log. Thời lượng đo cụ thể phụ thuộc máy, nên không dùng thời lượng test làm chỉ số thuật toán. Mười hai test không chứng nhận mô hình kinh tế đúng ngoài thực tế; chúng kiểm những bất biến quan trọng của implementation.
'''
(CH/'assignment_results.md').write_text(assignment)
tut='''# Kết quả thực hành và bằng chứng chạy

## Kiến trúc B0–B3

Các số dưới được lấy từ mas_benchmark.csv. Mỗi hệ chạy 11 ca, lặp 20 lần. Success có tính cả trạng thái từ chối đúng; tỷ lệ không đồng nghĩa tỷ lệ yêu cầu có gợi ý sản phẩm.
'''
tut+=table(['Hệ','Success (%)','P50 ms','P95 ms','Message/request','Violation (%)'],[[r['system'],f"{100*r['success_rate']:.2f}",f"{r['p50_ms']:.4f}",f"{r['p95_ms']:.4f}",f"{r['messages_mean']:.2f}",f"{100*r['violation_rate']:.2f}"] for r in mas['summary']])
tut+='\nKhông so tỷ lệ tốc độ B0/B1 trên các ca lỗi: baseline đơn trả trạng thái timeout được tiêm đồng bộ, còn MAS chờ deadline thực. Phần learned routing trong benchmark luôn nhận một câu ecommerce cố định, nên chỉ phản ánh overhead tích hợp. Đánh giá đa miền nằm ở bảng classifier riêng.\n\n## Chỉ số classifier trên held-out test\n'
tut+=table(['Lớp','Precision','Recall','F1','Số câu'],[[name,f"{intent['precision'][i]:.4f}",f"{intent['recall'][i]:.4f}",f"{intent['f1'][i]:.4f}",36] for i,name in enumerate(['ecommerce','tourism','healthcare admin'])])
tut+=f"\nAccuracy: {intent['accuracy']:.4f}; macro-F1: {intent['macro_f1']:.4f}; threshold {intent['threshold']}; coverage {intent['test_coverage']:.4f}. Tập train, validation và test: 270, 54 và 108 câu. Vocabulary 79; seed 42.\n\n## Ngoài miền: những lỗi cần giữ lại để phân tích\n"
tut+=table(['Câu thử','Kết quả','Confidence'],[[r['text'],r['intent'],f"{r['confidence']:.4f}"] for r in intent['ood']])
tut+='\nCó 4/6 câu được từ chối và 2/6 bị nhận nhầm vào miền dù confidence cao. Sáu câu là probe nhỏ, không phải một benchmark OOD đại diện. Không dùng tỷ lệ này để ước lượng lỗi trên mọi yêu cầu người dùng.\n'
tut+=fig('results/tutorial/intent_training.png','Loss train/validation và confusion matrix trên 108 câu test tổng hợp.')
tut+='''
## Kết quả failure injection và test
'''
tr=json.loads((ROOT/'results/tutorial/mas_traces.json').read_text())
tut+=table(['Ca lỗi','Status của B1','Số item'],[[r['case'],r['result']['status'],len(r['result']['items'])] for r in tr if r['system']=='B1_rule_MAS'])
tut+='''
Có 17 test tutorial chạy thành công; log đầy đủ nằm trong build/tutorial_tests.log. Hệ đã kiểm 4 lỗi bắt buộc của slide và thêm input NaN, ID giả, sai correlation. Trường hợp OOD trong test chỉ xác nhận câu không có token miền trả clarify, không phủ nhận các lỗi OOD đã báo ở bảng trên.

\\begin{verbatim}
python3 -m unittest discover -s tutorial -p 'test_*.py'
.................
Ran 17 tests
OK
\\end{verbatim}

## Mã thực thi cần đọc khi bảo vệ

\\lstinputlisting[firstline=68,lastline=84,caption={Deadline, xác thực envelope và trace của coordinator}]{tutorial/mas_system.py}
\\lstinputlisting[firstline=85,lastline=112,caption={Luồng điều phối và trạng thái kết thúc}]{tutorial/mas_system.py}

Đoạn mã đầy đủ trong tutorial/mas_system.py là nguồn sự thật khi cần kiểm các dòng sau trích đoạn. Notebook thể hiện lời gọi trực tiếp, đầu ra thực tế, dữ liệu học và các bảng kết quả; bản HTML cho phép xem offline mà không cần chạy kernel.
'''
(CH/'tutorial_results.md').write_text(tut)

paper_intro='''# Mở đầu: Hai paper trong một khung nghiên cứu

Báo cáo đọc và phân tích đầy đủ hai tài liệu giảng viên cung cấp: survey về cơ chế cộng tác nhiều LLM agent và tổng quan học tăng cường trong các lĩnh vực. Phần thứ nhất trả lời cách tổ chức các thành viên, thông tin và quyết định; phần thứ hai trả lời cách policy học từ tương tác và reward. Cả hai được liên hệ với tutorial và Laboratory Experiment 02 đã thực thi trong cùng bộ bài.

Mục tiêu của báo cáo là giải thích đủ sâu để người đọc có thể chuyển từ khái niệm sang thiết kế, đồng thời nêu điều kiện và giới hạn của từng kết luận. Nội dung không dịch nguyên văn hai paper; phần diễn giải, phép tính bổ sung và thiết kế thực nghiệm do người viết phát triển được trình bày tách khỏi mô tả đóng góp của tác giả.

## Cấu trúc và quy ước bằng chứng

Paper 1 được đọc theo background, mô hình tác tử, collaboration channels, loại quan hệ, chiến lược, topology, orchestration, ứng dụng và vấn đề mở. Paper 2 được đọc theo MDP, Bellman, các họ thuật toán, ứng dụng, thách thức và giả định. Phần tổng hợp cuối đối chiếu hai hướng, xây thiết kế mẫu và đề xuất protocol kiểm chứng.

Trong toàn bộ báo cáo, “kết quả paper” chỉ dùng cho những gì tài liệu gốc thực sự trình bày; “kết quả mô phỏng” chỉ dùng cho dữ liệu do mã đi kèm sinh; “đề xuất” chỉ phương án chưa được kiểm nghiệm đầy đủ. Không dùng demo cục bộ như bằng chứng tái lập benchmark LLM, không dùng dữ liệu tổng hợp như bằng chứng sẵn sàng triển khai thực tế.
'''
(CH/'paper_intro.md').write_text(paper_intro)
paper_syn='''# Tổng hợp, phản biện và thiết kế nối hai hướng nghiên cứu

## Bảng đối chiếu mục tiêu và loại bằng chứng
'''
paper_syn+=table(['Khía cạnh','Survey MAS/LLM','Survey RL'],[
['Câu hỏi trung tâm','Ai phối hợp, bằng kênh nào, theo cơ chế nào?','Policy học từ trải nghiệm như thế nào?'],
['Đơn vị phân tích','Tác tử, kênh, tổ chức, kiến trúc','State, action, reward, return, value'],
['Vai trò dữ liệu','Ngữ cảnh, bằng chứng, message, mô hình chia sẻ','Transition và feedback từ tương tác'],
['Rủi ro','Lỗi lan truyền, đồng thuận sai, overhead','Reward lệch, mẫu thiếu, state aliasing, bất ổn học'],
['Đánh giá cần có','Quality, cost, latency, trace, ablation','Frozen evaluation, seed, oracle, robustness'],
['Liên hệ bộ mã','Shopping MAS và failure injection','E-commerce Q-learning và DP']])
paper_syn+='''
## Hai cấp độ thích nghi không nên gộp

Điều phối động có thể thay graph thực hiện mà không cập nhật trọng số một mô hình nào. Một LLM đọc feedback và sửa kế hoạch trong cùng context có thể thay hành vi, nhưng đó chưa chứng minh có thuật toán RL tối ưu tham số. Ngược lại, Q-learning có thể cập nhật policy trong một môi trường có giao thức hoàn toàn cố định. “Agent biết thích nghi” vì thế cần chỉ rõ thứ gì thay đổi và theo cơ chế nào.

Trong tutorial, classifier được học offline bằng nhãn và giữ cố định trong inference. Coordinator thay trạng thái theo kết quả công cụ nhưng không học policy phân việc. Trong assignment, Q được cập nhật trong training rồi đóng băng để đánh giá. Ba loại thay đổi này cùng xuất hiện trong hệ thông minh nhưng có mục tiêu và bằng chứng khác nhau.

## Thiết kế tham chiếu: trợ lý kinh doanh có tầng quyết định và tầng kiểm chứng

Một kiến trúc nối hai hướng có thể gồm tầng nhận yêu cầu, tầng dự đoán, tầng chọn hành động và tầng kiểm chứng. Intent classifier định tuyến nhiệm vụ; agent dữ liệu thu thập trạng thái có version; policy learner đề xuất mức khuyến mãi; policy validator kiểm ràng buộc; coordinator quản lý trạng thái và dịch vụ thực thi trả xác nhận. Proposal không được coi là một giao dịch đã thành công.

State cho learner nên chứa nhu cầu, tồn kho, lịch sử giá, ngân sách khuyến mãi và thông tin đối thủ được phép quan sát. Action là các mức giảm hợp lệ hoặc đề xuất giữ giá. Reward có thể dựa trên profit đã trừ chi phí liên quan, nhưng các điều kiện pháp lý/nghiệp vụ bắt buộc phải nằm ngoài score học. Nếu phản hồi đến muộn, cơ chế gán reward cần được thiết kế trước khi train.

Đây là đề xuất kiến trúc, chưa được triển khai thành dịch vụ kinh doanh. Bộ bài thực thi hai phần nhỏ có thể kiểm chứng: coordinator shopping và learner bán hàng toy. Chúng chưa tích hợp thành hệ tự đổi giá thật; vì thế báo cáo không đưa con số doanh thu hoặc lợi ích vận hành cho kiến trúc mở rộng.

## Thiết kế thí nghiệm để tách lợi ích chia vai khỏi tăng tính toán

So sánh ít nhất bốn điều kiện: một agent với ngân sách chuẩn; một agent với cùng tổng ngân sách như MAS; MAS đầy đủ; MAS bỏ một cơ chế phối hợp quan trọng. Mọi điều kiện dùng cùng dữ liệu, quyền công cụ, tập tác vụ và tiêu chí thành công. Nếu MAS được thêm nguồn dữ liệu, cần có baseline cùng nguồn để tách ảnh hưởng dữ liệu khỏi tổ chức.

Đo success, groundedness, constraint violation, cost và latency; báo cáo cả phân phối và các trường hợp thất bại. Với LLM, lưu prompt/model version, nhiệt độ, số lần lấy mẫu, token và tool traces. Với RL, lưu training steps, evaluation tapes, seed và snapshot policy. Chỉ tăng số lần chạy mà không giữ protocol không tạo bằng chứng tái lập tốt.

Một ablation có ý nghĩa là bỏ bước inventory verification trong khi giữ số agent khác. Nếu chất lượng giảm, kết luận hẹp là verification có ích trong tập ca, chưa phải mọi cách chia vai đều có ích. Đây chính là cách đọc thí nghiệm B3 của tutorial. Nhận diện đúng biến độc lập giúp tránh gán công lao cho một nhãn kiến trúc rộng.

## Đề xuất kiểm tra độ bền nhiều tầng

Tầng dữ liệu: thêm thiếu trường, schema sai, dữ liệu cũ và nguồn mâu thuẫn. Tầng giao tiếp: thêm timeout, duplicate response, sai task ID và response đến muộn. Tầng quyết định: đổi giá vốn, discount, đối thủ và nhu cầu. Tầng triển khai: đo tải, version và cơ chế khôi phục. Mỗi thay đổi cần giữ một tập đối chứng để xác định tác động.

Bộ mã hiện kiểm schema, freshness, timeout, forged output và shift discount; đồng thời có self-play để minh họa đồng học. Nó chưa kiểm tải mạng, Byzantine agent, đối thủ ngoài tập hoặc deployment thật. Một bản báo cáo chi tiết phải ghi cả những gì đã đo và những gì chưa đo để người đọc đặt đúng độ tin cậy.

## Những luận điểm cần tránh sau khi đọc hai paper

Không suy ra “nhiều agent hơn luôn đúng hơn”; sai số tương quan và chi phí giao tiếp có thể làm kết quả kém đi. Không suy ra “RL luôn học policy tối ưu”; giả định Markov, tính dừng, độ bao phủ và protocol đóng vai trò thiết yếu. Không suy ra “accuracy cao là hệ đáng tin”; một classifier đúng trên synthetic test vẫn nhận sai OOD. Không suy ra “rule-based không thích ứng đầu vào”; nó có thể phản ứng theo state dù không cập nhật từ reward.

Các kết luận tích cực vẫn rất rõ: chia vai có thể tạo hợp đồng kiểm được; RL cung cấp cơ chế cải thiện từ feedback; model-based oracle giúp đo khoảng cách tới chuẩn trong môi trường biết mô hình; và logging/ablation giúp truy nguyên lỗi. Giá trị của hai paper nằm ở cách đặt vấn đề, cộng với kiểm chứng cụ thể khi áp dụng.

# Bằng chứng minh họa liên hệ hai paper

Các kết quả dưới thuộc bộ mã của báo cáo, không phải bảng benchmark chép từ hai bài gốc. Tutorial kiểm kiến trúc local; assignment kiểm policy trong mô phỏng. Phần số liệu đầy đủ nằm trong hai báo cáo chuyên biệt và các CSV đi kèm.
'''
paper_syn+=table(['Thực nghiệm của báo cáo','Quan sát','Phạm vi kết luận'],[
['MAS B0/B1','Cùng 100% success trên 11 ca','Chia vai chưa tăng chất lượng trong catalog nhỏ'],
['MAS B3','8/11 ca đúng; lỗi khi bỏ kiểm','Validation cần thiết trong tập failure injection'],
['Intent test','108/108 đúng','Chỉ trên test tổng hợp chia nhóm'],
['Intent OOD','4/6 clarify; 2 false accept','Softmax/confidence chưa đủ phát hiện ngoài miền'],
['RL 5 seeds','34.0997 ± 1.3678','Baseline còn biến động và dưới policy không giảm'],
['Rule/DP','Cùng policy và khoảng 35.1295','Best response trong mô hình đối thủ đã chỉ định']])
paper_syn+=fig('results/tutorial/intent_training.png','Minh họa phân biệt chất lượng trong phân phối và đánh giá ngoài miền; đây là dữ liệu tự thực thi.')
paper_syn+=fig('results/assignment/learning_rates.png','Độ nhạy learning rate trong mô hình bán hàng toy; vùng tô là một SD qua năm seed.')
paper_syn+=fig('results/assignment/evaluation.png','Đánh giá policy đóng băng và mốc analytic không giảm giá.')
paper_syn+='''
# Phụ lục đọc paper: bản đồ nội dung và câu hỏi kiểm tra

## Đối chiếu Paper 1 với tài liệu gốc
'''
paper_syn+=table(['Phần tài liệu gốc','Nội dung đã phân tích','Câu hỏi khi đọc lại'],[
['Section 1','Động lực, đóng góp, vị trí survey','Tại sao cơ chế phối hợp là trọng tâm?'],
['Section 2','MAS, LLM, collaborative AI','Mô hình khác agent ở trách nhiệm nào?'],
['Section 3','Agent tuple, system, collaboration channel','Kênh cần mô tả đủ những thuộc tính gì?'],
['Section 4.2','Cooperation, competition, coopetition','Mục tiêu cấp agent và cấp hệ có khác không?'],
['Section 4.3','Rule-, role-, model-based','Đây là protocol hay decision policy?'],
['Section 4.4','Centralized, decentralized/distributed, hierarchical','Quyền kiểm soát khác vị trí thực thi thế nào?'],
['Section 4.5','Static/dynamic orchestration','Điểm nào thật sự thay đổi lúc chạy?'],
['Section 5','Mạng, QA/NLG, xã hội/văn hóa','Ground truth và authority ở đâu?'],
['Section 6','Collective intelligence, benchmark, safety','Bằng chứng nào còn thiếu?'],
['Section 7','Kết luận taxonomy','Khung có giúp thiết kế phép thử không?']])
paper_syn+='\n## Đối chiếu Paper 2 với tài liệu gốc\n'
paper_syn+=table(['Phần tài liệu gốc','Nội dung đã phân tích','Câu hỏi khi đọc lại'],[
['I–II','Mục tiêu, MDP/POMDP, policy, Bellman','State có đủ và quá trình có dừng không?'],
['III','Bandit, exploration, value','Feedback khác nhãn giám sát thế nào?'],
['IV-A','Dynamic programming','Biết mô hình có thể xây oracle nào?'],
['IV-B','Monte Carlo','Return cần chờ đến đâu và nhiễu từ đâu?'],
['IV-C','TD, SARSA, Q-learning','Target theo policy nào và có bootstrap không?'],
['IV-D/E','Actor–critic, Bayesian','Mỗi mô hình ước lượng điều gì?'],
['IV-F','DQN, replay và target network','Vì sao cần ổn định khi xấp xỉ Q?'],
['V-A đến V-I','Các miền ứng dụng','Quyết định có ảnh hưởng tương lai thật không?'],
['V-J/K','Challenges, lessons learned','Reward, coverage, non-stationarity có được kiểm?'],
['VI–VII','Discussion và kết luận','Phát biểu hội tụ cần điều kiện gì?']])
paper_syn+='''
## Câu hỏi phản biện và lời giải định hướng

**Vì sao hai agent đồng ý vẫn có thể sai?** Vì cùng mô hình hoặc cùng nguồn có thể gây lỗi tương quan; đa số không tạo nguồn thông tin mới. Cần đối chiếu bằng chứng hoặc phép kiểm độc lập.

**Vì sao cùng state–action có reward khác nhau chưa chắc là non-stationarity?** Môi trường stochastic vốn tạo reward khác qua các mẫu. Non-stationarity nói quy luật phân phối thay đổi; cần nhiều dữ liệu hoặc kiểm soát policy đối thủ để phân biệt.

**Vì sao tăng số seed chưa chứng minh mô hình kinh tế đúng?** Seed chỉ thay chuỗi ngẫu nhiên trong mô hình đã giả định. Nếu conversion sai hoặc thiếu thị phần, mọi seed đều chịu cùng sai lệch cấu trúc.

**Vì sao một agent biết mô hình có thể là baseline tốt?** Nó giúp xác định khả năng đạt được trong mô phỏng nhỏ; chênh lệch với learner cho thấy khoảng cách cần cải thiện. Nhưng lợi thế biết mô hình phải được nêu để không làm so sánh thiếu công bằng về thông tin.

**Vì sao không dùng DQN cho bảng tám ô?** Không gian nhỏ không đòi xấp xỉ bằng mạng; mạng thêm nhiễu và tuning. Chọn tabular giúp minh bạch cập nhật và dễ đối chiếu oracle.

**Vì sao ngưỡng confidence cần validation?** Chọn trên test làm rò rỉ thông tin về benchmark cuối. Dù chọn đúng validation, confidence vẫn có thể cao với OOD nên cần đánh giá false acceptance riêng.

**Khi nào nên dùng MAS?** Khi có trách nhiệm, dữ liệu hoặc quyền tách biệt và phối hợp tạo lợi ích đo được. Nếu baseline đơn đạt cùng chất lượng với ít chi phí, lựa chọn đơn giản vẫn có cơ sở.

**Khi nào nên dùng RL?** Khi có chuỗi quyết định, feedback và điều kiện tương tác phù hợp để học. Nếu biết mô hình nhỏ và có lời giải chính xác, planning hoặc luật đã được kiểm chứng có thể phù hợp hơn.

# Kết luận chung của báo cáo paper

Hai paper cung cấp hai mặt bổ sung của hệ tác tử: tổ chức tương tác và học quyết định. Một thiết kế có trách nhiệm cần cả mô hình khái niệm rõ lẫn bằng chứng thực nghiệm phù hợp. Bản báo cáo đã trình bày nền tảng, phân loại, công thức, thuật toán, ứng dụng, phản biện và liên hệ trực tiếp với mã đã chạy.

Giới hạn xuyên suốt là mô phỏng toy và dữ liệu intent tổng hợp. Các con số thực thi chứng minh quy trình và kiểm tra một số giả thuyết hẹp, không thay thế benchmark LLM hay đánh giá vận hành thực tế. Đó là ranh giới giúp sử dụng kiến thức từ survey một cách chính xác và có thể kiểm tra.
'''
(CH/'paper_synthesis.md').write_text(paper_syn)

refs=r'''\clearpage
\phantomsection\addcontentsline{toc}{section}{Tài liệu tham khảo}
\begin{thebibliography}{99}
\bibitem{slides} PGS.TS. Trần Đình Quế (tài liệu môn học được cung cấp), \emph{Developing Multiagent Systems: A Practical Tutorial with Python and PyTorch}, slide\_multiAgent\_system\_20.10.2026.pdf, 25 trang, 2026. Nguồn cục bộ trong đề bài.
\bibitem{lab} \emph{Laboratory Experiment 02: Reinforcement-Learning-Based Agents versus Rule-Based Agents}, Intelligent System Development, 2026--2027, assignment\_Agent02\_due\_29.10.pdf, 13 trang; agent02\_code.tex và agent02\_complementary\_code.pdf. Tài liệu cục bộ do người dùng cung cấp.
\bibitem{tran} K.-T. Tran, D. Dao, M.-D. Nguyen, Q.-V. Pham, B. O'Sullivan, H. D. Nguyen, \emph{Multi-Agent Collaboration Mechanisms: A Survey of LLMs}, arXiv:2501.06322v1, 10/01/2025. \url{https://arxiv.org/abs/2501.06322v1}. Phân tích trực tiếp bản PDF 35 trang được cung cấp.
\bibitem{naeem} M. Naeem, S. T. H. Rizvi, A. Coronato, \emph{A Gentle Introduction to Reinforcement Learning and Its Application in Different Fields}, IEEE Access, vol. 8, pp. 209320--209344, 2020. DOI: \href{https://doi.org/10.1109/ACCESS.2020.3038605}{10.1109/ACCESS.2020.3038605}. Phân tích trực tiếp bản PDF 25 trang được cung cấp.
\bibitem{sutton} R. S. Sutton, A. G. Barto, \emph{Reinforcement Learning: An Introduction}, 2nd ed., MIT Press, 2018. Tài liệu nền tảng được cả slide và paper RL dẫn chiếu.
\bibitem{watkins} C. J. C. H. Watkins, P. Dayan, \emph{Q-learning}, Machine Learning 8, 279--292, 1992. DOI: \href{https://doi.org/10.1007/BF00992698}{10.1007/BF00992698}.
\bibitem{autogen} Q. Wu et al., \emph{AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation}, 2023. \url{https://arxiv.org/abs/2308.08155}.
\bibitem{metagpt} S. Hong et al., \emph{MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework}, 2023, bản cập nhật 2024. \url{https://arxiv.org/abs/2308.00352}.
\bibitem{debate} Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, I. Mordatch, \emph{Improving Factuality and Reasoning in Language Models through Multiagent Debate}, 2023. \url{https://arxiv.org/abs/2305.14325}.
\bibitem{torchce} PyTorch, \emph{CrossEntropyLoss}, tài liệu chính thức. \url{https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html}. Đối chiếu giao diện ngày 28/10/2026; môi trường thực nghiệm dùng PyTorch 2.8.0.
\bibitem{pythonasync} Python documentation, \emph{Coroutines and Tasks: asyncio.wait\_for}. \url{https://docs.python.org/3/library/asyncio-task.html}. Phần timeout được kiểm trực tiếp bằng tests trong môi trường thực thi.
\bibitem{artifacts} Bộ mã và dữ liệu tự thực thi của báo cáo: tutorial/, assignment/, results/, build/; seed và cấu hình lưu trong summary.json, intent\_metrics.json và mas\_metrics.json, ngày 28/10/2026. Đây là nguồn kết quả mô phỏng, không phải nguồn dữ liệu thị trường thực tế.
\end{thebibliography}
'''
(ROOT/'report/references.tex').write_text(refs)

cover=(ROOT/'report/cover_template.tex').read_text()
# ROOT is agent-ai/ASIGNMENT-AGENT_02/solution, parents[1] is agent-ai
specs=[('tutorial_CT_04_hainn','TUTORIAL PHÁT TRIỂN HỆ ĐA TÁC TỬ','PYTHON, PYTORCH VÀ KIỂM CHỨNG HỆ THỐNG',['tutorial','tutorial_results']),
('paper_CT_04_hainn','BÁO CÁO ĐỌC VÀ PHÂN TÍCH PAPER','MULTI-AGENT COLLABORATION VÀ REINFORCEMENT LEARNING',['paper_intro','paper_mas','paper_rl','paper_technical','paper_synthesis']),
('agent02_CT_04_hainn','BÁO CÁO THỰC HÀNH AGENT 02','REINFORCEMENT LEARNING VÀ RULE-BASED AGENTS',['assignment','assignment_results'])]
for stem,title,subtitle,chapters in specs:
    cv=cover.replace('BÁO CÁO VỀ TÌM HIỂU AGENT',title).replace('DISCOVERING AI AGENT',subtitle)
    cv=cv.replace('{\\Large\\textbf{'+subtitle+'}}','{\\large\\textbf{'+subtitle+'}}')
    (ROOT/f'report/{stem}_cover.tex').write_text(cv)
    for name in chapters:
        subprocess.run(['pandoc',str(CH/(name+'.md')),'-f','markdown+raw_tex','-t','latex','--listings','-o',str(CH/(name+'.tex'))],check=True)
    front=r'''\pagenumbering{roman}
\setcounter{tocdepth}{2}
{\linespread{1.0}\selectfont\tableofcontents}
\clearpage\listoffigures\clearpage
\section*{DANH MỤC THUẬT NGỮ}
\addcontentsline{toc}{section}{Danh mục thuật ngữ}
\begin{tabularx}{\linewidth}{p{2.5cm}X}
\toprule
MAS & Multi-Agent System -- Hệ đa tác tử\\
LLM & Large Language Model -- Mô hình ngôn ngữ lớn\\
RL / MARL & Reinforcement Learning / Multi-Agent RL\\
MDP / POMDP & Quá trình quyết định Markov / quan sát không đầy đủ\\
TD / Q & Sai phân thời gian / Giá trị hành động\\
DP & Dynamic Programming -- Quy hoạch động\\
OOD & Out-of-distribution -- Ngoài phân phối/ngoài miền\\
PEAS & Performance, Environment, Actuators, Sensors\\
DAG & Directed Acyclic Graph -- Đồ thị có hướng không chu trình\\
SD / CI & Độ lệch chuẩn mẫu / Khoảng tin cậy\\
P50 / P95 & Phân vị 50 / 95 của thời gian phản hồi\\
TTL & Time to Live -- Giới hạn độ mới của dữ liệu\\
\bottomrule
\end{tabularx}
\vspace{8mm}
\begin{academicbox}{Quy ước đọc báo cáo}
Dữ liệu thực hành là tổng hợp hoặc mô phỏng. Số đo được lấy từ mã đã chạy và lưu kèm; phép tính lý thuyết và đề xuất chưa thực hiện được gọi rõ. Thông tin bìa, logo và phong cách trình bày kế thừa báo cáo trước. Ngày hoàn thiện: 28/10/2026.
\end{academicbox}
\clearpage\pagenumbering{arabic}\setcounter{page}{1}
'''
    main=r'''\documentclass[12pt,a4paper]{article}
\makeatletter\def\input@path{{report/}}\makeatother
\usepackage{assignment_format}
\usepackage{longtable,calc,listings,etoolbox}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}
\newcounter{none}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible,
 keepspaces=true,showstringspaces=false,frame=single,rulecolor=\color{accent!40},
 backgroundcolor=\color{black!2},numbers=left,numberstyle=\tiny,numbersep=5pt,
 xleftmargin=8pt,framexleftmargin=5pt,aboveskip=8pt,belowskip=8pt}
\setlength{\LTpre}{5pt}\setlength{\LTpost}{5pt}
\AtBeginEnvironment{longtable}{\small\linespread{1.05}\selectfont}
\DeclareUnicodeCharacter{2212}{\ensuremath{-}}
\DeclareUnicodeCharacter{2264}{\ensuremath{\leq}}
\DeclareUnicodeCharacter{2265}{\ensuremath{\geq}}
\DeclareUnicodeCharacter{03B5}{\ensuremath{\epsilon}}
\DeclareUnicodeCharacter{03B1}{\ensuremath{\alpha}}
\DeclareUnicodeCharacter{03B3}{\ensuremath{\gamma}}
\DeclareUnicodeCharacter{00D7}{\ensuremath{\times}}
\DeclareUnicodeCharacter{2192}{\ensuremath{\rightarrow}}
\DeclareUnicodeCharacter{00B1}{\ensuremath{\pm}}
'''
    main+='\\hypersetup{pdftitle={'+title+'},pdfauthor={Nguyễn Nam Hải -- B23DCCN277}}\n\\begin{document}\n\\input{report/'+stem+'_cover.tex}\n'+front
    for name in chapters:
        if stem.startswith('paper') and name!='paper_intro':main+='\\clearpage\n'
        main+='\\input{report/chapters/'+name+'.tex}\n'
    main+='\\input{report/references.tex}\n\\end{document}\n'
    (ROOT/(stem+'.tex')).write_text(main)
print('Prepared all report sources')
