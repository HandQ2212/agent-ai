# DISCOVERING AI AGENT

Bản mở rộng báo cáo tiếng Việt, mã định danh `hainn`, tên tệp theo đề:
`agent01_CT_04_hainn.pdf`.

## Các tệp chính

- `agent01_CT_04_hainn.pdf`: PDF 35 trang: bìa, mục lục, 15 trang lý thuyết, 16 trang thực hành/tổng kết và 2 trang nguồn tham khảo.
- `agent01_CT_04_hainn.tex`: LaTeX chính; cần ba tệp `theory_extended.tex`, `practice_extended.tex`, `references_extended.tex` đi kèm.
- `agent01_CT_04_hainn.ipynb`: notebook có 17 cell code đã chạy, lưu đầy đủ output, gồm 3 bài thực hành.
- `agent01_CT_04_hainn_code.py`: toàn bộ 389 dòng code thực thi xuất từ notebook; chạy được với Python và Matplotlib.
- `agent01_CT_04_hainn_notebook.html`: bản HTML của code và output thực thi, xem được bằng trình duyệt, không cần mạng.
- `screenshots/cell_1.png` … `cell_17.png`: đủ 17 ảnh chụp code và output đã chèn trong báo cáo.
- `assets/q_learning_results.png`: đồ thị reward huấn luyện và quỹ đạo chính sách Q-learning, sinh từ dữ liệu chạy thật.
- `build_notebook.py` và `notebook_extra.py`: định nghĩa, tạo và thực thi các cell bằng IPython, lưu notebook và HTML. Output được thu từ thực thi thật, không viết tay.
- `capture_notebook.py`: dùng một phiên Chrome headless để chụp mọi cell HTML.

Ba bài thực hành: (1) goal-based agent tìm đường và tái lập kế hoạch, dựa trên khái niệm IBM [2]; (2) trợ lý tra cứu dùng hai công cụ search/read, dẫn chứng, cache và schema; (3) learning agent Q-learning được huấn luyện thật trên GridWorld với 3 seed. Bài 2 dùng retrieval lexical và trả lời trích xuất, không phải tái lập mô hình RAG sinh văn bản. Không có lời gọi LLM hoặc output API giả lập; không cần API key. Bản đồ và kho quy định đều là dữ liệu giả lập, được ghi rõ trong báo cáo.

## Chạy notebook

Mở tệp `.ipynb` trong Jupyter Notebook/JupyterLab/VS Code, chọn kernel Python 3, rồi chọn **Restart Kernel and Run All Cells**. Bài 1–2 dùng thư viện chuẩn; bài 3 thêm Matplotlib để vẽ hình. Có thể chạy trực tiếp `python3 agent01_CT_04_hainn_code.py`.

Để dựng lại notebook và HTML, cần `nbformat`, `IPython`, `pygments`, `matplotlib`:

```sh
mkdir -p build screenshots
python3 build_notebook.py
```

Các ảnh PNG là ảnh Chrome headless chụp các HTML riêng của từng cell. Khung ảnh bỏ tiêu đề lặp và khoảng trống, giữ nguyên code/output. Sau khi sửa code, chạy `python3 capture_notebook.py` trước khi compile. Script chụp cần `websocket-client`, Chrome và quyền chạy trình duyệt cục bộ; đường dẫn Chrome trong script mặc định là macOS và có thể đổi theo hệ điều hành. Cổng DevTools chỉ lắng nghe trên localhost trong thời gian chụp; script đóng phiên Chrome của nó khi xong.

## Biên dịch LaTeX

Cần TeX Live/MiKTeX có XeLaTeX, các gói `fontspec`, `tikz`, `hyperref`, `bookmark`, `caption`, cùng font Times New Roman, Arial và Courier New. Các font được cấu hình ở đầu `.tex`; có thể thay bằng font Unicode tiếng Việt tương đương nếu máy thiếu font.

Chạy trong thư mục chứa `.tex` và `screenshots/`:

```sh
xelatex -interaction=nonstopmode -halt-on-error agent01_CT_04_hainn.tex
xelatex -interaction=nonstopmode -halt-on-error agent01_CT_04_hainn.tex
```

Hai lượt biên dịch giải quyết số trích dẫn và mục lục. Các nguồn [1]–[4] giữ đúng thứ tự đề bài; có 20 nguồn bổ sung, tổng 24 tài liệu, đều được dẫn trong nội dung. Truy cập/đối chiếu nguồn ngày 23/10/2026. Các ví dụ thiết kế, nhận định và số liệu mô phỏng được phân biệt với thông tin trích nguồn.

## Kết quả kiểm tra

| Ca | Trạng thái | Lần gọi công cụ |
|---|---|---:|
| Tĩnh | `success` | 3 |
| Động (đóng B–D) | `success` | 5 |
| Hết ngân sách | `budget_exhausted` | 1 |
| A bị cô lập | `unreachable` | 2 |
| Ban đầu đã ở F | `success` | 0 |

Ca động đi A–B–C–E–F: 4 bước thành công, 5 lần gọi công cụ, 2 lần lập kế hoạch. Bài 1 đạt 5/5 ca xác định.

Bài 2 đạt 8/8 kiểm tra về dẫn chứng, cache, thiếu bằng chứng, ngân sách, input rỗng, ranking và schema.

Bài 3 huấn luyện 3 seed (7, 42, 2026), mỗi seed 2.500 episode. Mỗi chính sách đóng băng đạt 100/100 episode đánh giá, đường đi 8 bước đúng oracle BFS; baseline ngẫu nhiên đạt 48/100, trung bình 80,23 bước trên toàn bộ episode. Có kiểm tra terminal bootstrap, đường hợp lệ và Q không thay đổi trong đánh giá. Đây là kết quả trên một lưới tĩnh, không phải đánh giá khái quát trên các bản đồ khác.

## Kiến thức mở rộng

MDP/POMDP, LLM agent và workflow, hợp đồng công cụ, bộ nhớ và reflection, RAG, tìm kiếm và lập kế hoạch, đa tác tử, Q-learning, AgentBench/WebArena/SWE-bench, prompt injection và vòng đời triển khai. Các nghiên cứu gốc có liên kết trong danh mục của PDF và LaTeX.
