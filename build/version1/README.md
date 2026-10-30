# DISCOVERING AI AGENT

Bài báo cáo tiếng Việt, mã định danh `hainn`, tên tệp theo đề:
`agent01_CT_04_hainn.pdf`.

## Các tệp chính

- `agent01_CT_04_hainn.pdf`: PDF đã biên dịch, 12 trang: bìa, 6 trang tìm hiểu, 4 trang thực hành, tài liệu tham khảo.
- `agent01_CT_04_hainn.tex`: mã LaTeX.
- `agent01_CT_04_hainn.ipynb`: notebook có 6 cell code đã chạy và lưu output; 5 ca kiểm tra đều đạt.
- `agent01_CT_04_hainn_notebook.html`: bản HTML của code và output thực thi, xem được bằng trình duyệt, không cần mạng.
- `screenshots/cell_1.png` … `cell_6.png`: ảnh chụp code và output đã chèn trong báo cáo.
- `build_notebook.py`: tạo và thực thi các cell bằng IPython, lưu notebook và HTML. Output được thu từ thực thi thật, không viết tay.

Notebook tự triển khai mô hình agent theo mục tiêu dựa trên bài IBM [2], theo lựa chọn đã thống nhất. Không phải code sao chép từ một tutorial IBM cụ thể; không gọi LLM, không dùng RL, không cần API key. Đồ thị và biến cố là dữ liệu mô phỏng.

## Chạy notebook

Mở tệp `.ipynb` trong Jupyter Notebook/JupyterLab/VS Code, chọn kernel Python 3, rồi chọn **Restart Kernel and Run All Cells**. Code thực nghiệm chỉ dùng thư viện chuẩn Python; không cần cài thư viện học máy.

Để dựng lại tệp notebook và HTML bằng script, cần `nbformat`, `IPython`, `pygments`:

```sh
mkdir -p build screenshots
python3 build_notebook.py
```

Các ảnh PNG hiện có là ảnh Chrome headless chụp các HTML riêng của từng cell. Đầu và cuối ảnh được cắt khoảng trống/tiêu đề lặp để tăng diện tích hiển thị code, không sửa nội dung code hoặc output. Chạy script trên chỉ cập nhật notebook và HTML, không tự cập nhật PNG; nếu sửa code, cần chụp lại ảnh trước khi compile PDF.

## Biên dịch LaTeX

Cần TeX Live/MiKTeX có XeLaTeX, các gói `fontspec`, `tikz`, `hyperref`, `bookmark`, `caption`, cùng font Times New Roman, Arial và Courier New. Các font được cấu hình ở đầu `.tex`; có thể thay bằng font Unicode tiếng Việt tương đương nếu máy thiếu font.

Chạy trong thư mục chứa `.tex` và `screenshots/`:

```sh
xelatex -interaction=nonstopmode -halt-on-error agent01_CT_04_hainn.tex
xelatex -interaction=nonstopmode -halt-on-error agent01_CT_04_hainn.tex
```

Hai lượt biên dịch giải quyết số trích dẫn. Các nguồn được đánh số [1]–[4] đúng thứ tự đề bài; tài liệu nghiên cứu bổ sung là [5]–[7]. Truy cập nguồn ngày 23/10/2026. Các ví dụ thiết kế và nhận xét của báo cáo được phân biệt với thông tin trích nguồn.

## Kết quả kiểm tra

| Ca | Trạng thái | Lần gọi công cụ |
|---|---|---:|
| Tĩnh | `success` | 3 |
| Động (đóng B–D) | `success` | 5 |
| Hết ngân sách | `budget_exhausted` | 1 |
| A bị cô lập | `unreachable` | 2 |
| Ban đầu đã ở F | `success` | 0 |

Ca động đi A–B–C–E–F: 4 bước thành công, 5 lần gọi công cụ, 2 lần lập kế hoạch. 5/5 là số ca xác định đã kiểm tra, không phải ước lượng độ tin cậy tổng quát.
