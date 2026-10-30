# AGENT02 — Tutorial, Paper và Assignment

Bộ bài của **Nguyễn Nam Hải — B23DCCN277**, kế thừa thông tin và mẫu bìa PTIT từ báo cáo trước. Mã tên tệp: `CT_04_hainn`; bìa giữ lớp D23CTPM01/nhóm học phần CT01 như bản trước.

## Đọc và sử dụng

- `tutorial_CT_04_hainn.pdf`: tutorial tiếng Việt đủ 20 unit và năm exercise; MAS shopping, PyTorch train thật, failure injection, so sánh B0–B3.
- `paper_CT_04_hainn.pdf`: phân tích **cả hai paper** được cung cấp, gồm nền tảng, mô hình, taxonomy, thuật toán, ứng dụng, phản biện, 18 chuyên đề kỹ thuật, phép tính, tổng hợp và đối chiếu nguồn.
- `agent02_CT_04_hainn.pdf`: báo cáo nộp Laboratory 02, đủ thí nghiệm A–E và lời giải 10 câu, kết quả nhiều seed, robustness và cải tiến DP.
- `tutorial_CT_04_hainn.ipynb`, `agent02_CT_04_hainn.ipynb`: notebook đã thực thi thật, lưu đủ output. Hai bản `*_notebook.html` xem offline.
- `tutorial/demo_slides.html`: trình bày offline, mở bằng trình duyệt; phím mũi tên/Space để đổi slide.
- `COVERAGE.md`: bản đồ yêu cầu → phần báo cáo → nguồn/bằng chứng.
- `artifact_manifest.json`: danh sách tệp, SHA256 và thông tin PDF/notebook.

Ba PDF có bìa khung đôi, logo PTIT gốc, font tiếng Việt VNR/T5 12pt, A4, lề và header/footer theo báo cáo trước, mục lục, hình và tài liệu tham khảo. File `.tex` và Markdown trong `report/chapters/` cho phép chỉnh nội dung.

## Cài môi trường

```sh
cd ASIGNMENT-AGENT_02/solution
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Môi trường thực tế đã kiểm: Python 3.9.6, PyTorch CPU 2.8.0; phiên bản khác lưu trong `environment_versions.json`. Với cài mới nên dùng Python 3.10 trở lên và bản PyTorch tương thích. Không cần GPU, API key hoặc kết nối dịch vụ bên ngoài cho các thí nghiệm. Pandoc/TeX Live chỉ cần khi dựng lại PDF.

## Tutorial

```sh
python3 tutorial/slide_baseline.py
python3 tutorial/mas_system.py
python3 tutorial/train_intent.py
python3 tutorial/evaluate_mas.py
python3 -m unittest discover -s tutorial -p 'test_*.py'
```

Bản `slide_baseline.py` chạy riêng luồng gốc của slide, năm kiểm tra đều qua; bản mở rộng tách riêng để đọc tiến trình cải tiến.

Train trước khi chạy router/evaluation nếu không dùng checkpoint kèm. `results/tutorial/` chứa dataset CSV 432 câu, dự đoán test, training loss, checkpoint `intent_model.pt`, metrics, benchmark raw và trace.

- Dữ liệu intent chia theo họ động từ 270/54/108, vocabulary chỉ từ train. Test vẫn dùng các đối tượng cùng từ vựng miền, nên là bài tổng hợp tương đối dễ.
- Accuracy và macro-F1 trên test bằng 1.0; **hai trong sáu probe ngoài miền bị chấp nhận nhầm**. Có ngưỡng và abstention, chưa có OOD detector đáng tin.
- B0/B1/B2 cùng đạt 11/11 ca. B3 đạt 8/11. Có 17 test qua.
- B2 benchmark luôn dùng cùng một câu ecommerce để định tuyến; bảng này chỉ đo overhead tích hợp. Định tuyến đa miền được đánh giá riêng.
- B0 trả lỗi timeout mô phỏng đồng bộ; B1/B2/B3 dùng `asyncio.wait_for` thật. Không dùng tỷ lệ P95 giữa chúng để kết luận tốc độ kiến trúc trong môi trường dịch vụ thật.

## Assignment và chạy lại kết quả

```sh
python3 assignment/agent02_experiment.py
python3 assignment/analyze_exact.py
python3 -m unittest discover -s assignment -p 'test_*.py'
```

Chương trình đầy đủ chạy 36 lượt training: 25 cấu hình/seed sensitivity, một baseline minh họa 42, năm retrain discount 40% và năm self-play; 5.000 episode × 20 bước mỗi lượt, tổng 3.600.000 environment steps. Self-play có hai cập nhật Q mỗi bước. Evaluation riêng 500 episode, Q đóng băng và epsilon bằng 0. Tất cả raw CSV nằm ở `results/assignment/`.

Seed chính 11, 22, 33, 44, 55. Các policy comparison dùng cùng rule opponent và cùng demand/uniform tape; evaluation seed = 800000 + training seed. Discount robustness thay 20% bằng 40%. `summary.json` lưu config, Q-tables, aggregate và version; `.npy` lưu Q seed 42. `exact_policy_values.csv` chứa kỳ vọng không lấy mẫu của mọi policy đã học.

Kết quả chính: baseline RL 34.0997 ± 1.3678 reward/step (mean ± sample SD qua seed); rule/never/DP khoảng 35.1295 trên tape đánh giá. Trong mô hình này best response với rule là không giảm giá, kỳ vọng lý thuyết 35. Không được suy ra RL luôn kém luật trên các thị trường khác.

`reference_agent02.py` giữ nguyên code từ tệp đề `agent02_code.tex`. Bản gốc đã chạy riêng baseline seed 42; kết quả ở `reference_original_42_*`. Nó khác kết quả bản mở rộng cùng seed vì bản mở rộng tách RNG stream, cách phá hòa và evaluator. Hai bản cùng mô hình phân phối, không tái lập bit-for-bit. Mã tham chiếu đầy đủ còn có thể chạy bằng `python3 assignment/reference_agent02.py` (nó tạo thư mục output riêng theo code gốc).

## Notebook

Mở notebook bằng Jupyter/VS Code và **Restart Kernel and Run All** trong môi trường đã cài dependencies. Notebook tutorial chạy 14 cell code, notebook assignment 15 cell code; có demo, assertion, hình/bảng và chạy tests. Các bảng lớn đọc artifact từ full experiment; không giả là vừa train lại toàn bộ.

- `RETRAIN=False` trong tutorial bảo toàn checkpoint đã nộp.
- `RUN_FULL_EXPERIMENT=False` trong assignment bảo toàn kết quả 36 training runs.
- Muốn chạy lại toàn bộ, bật cờ hoặc dùng script dòng lệnh bên trên.

`build_notebooks.py` đã thực thi code bằng IPython trong cùng tiến trình và lưu output thật; môi trường sandbox không cho mở socket kernel Jupyter cục bộ nên không dùng nbclient server. Notebook vẫn có kernel metadata Python 3 tiêu chuẩn để chạy thông thường ở máy người dùng. Không có output viết tay hoặc API LLM giả.

## Dựng lại tài liệu

Từ `solution/`, sau khi có kết quả:

```sh
python3 build_documents.py
python3 build_notebooks.py
python3 build_reports.py
python3 package_solution.py
```

`build_documents.py` cần Pandoc; `build_reports.py` cần pdfLaTeX/TeX Live với T5, babel tiếng Việt, TikZ, tcolorbox, listings, longtable. Ba lượt biên dịch giải quyết mục lục và tham chiếu. `build/` giữ log; PDF cuối sao chép ra thư mục solution. `package_solution.py` cập nhật manifest và tạo ZIP ở thư mục cha; nó không sửa các tài liệu đề hoặc báo cáo Agent01.

## Phạm vi và tính trung thực kết quả

Catalog, kho, câu intent và thị trường đều synthetic. Không có LLM inference, thanh toán, dữ liệu bệnh nhân hoặc triển khai lên dịch vụ. Các nhận định về paper dựa trực tiếp trên PDF cung cấp, cùng nguồn nghiên cứu/tài liệu chính thức được dẫn trong báo cáo. Hình kết quả do Matplotlib vẽ từ output thực thi. Các phương án chưa chạy được gọi là đề xuất, không có số liệu tưởng tượng.
