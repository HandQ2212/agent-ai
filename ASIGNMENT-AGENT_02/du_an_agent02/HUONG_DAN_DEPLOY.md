# Đưa Agent 02 lên GitHub và Render

Bản hướng dẫn này giả sử `du_an_agent02` là **gốc repository**. Ứng dụng dùng một Render Web Service chạy cả frontend và backend Python; không dùng Static Site vì các API cần Python.

## 1. Đẩy dự án lên GitHub

1. Trên GitHub tạo một repository mới, ví dụ `agent02-lab`. Với các lệnh dưới đây, chọn repository **trống**, chưa tạo README, `.gitignore` hay license trên GitHub.
2. Mở terminal trong `du_an_agent02`:

```sh
cd /Users/handq2212/DaiHoc/Nam4/LTHTTM/agent-ai/ASIGNMENT-AGENT_02/du_an_agent02
git init -b main
git add .
git status
git commit -m "Add Agent 02 web app"
```

3. Trên trang repository vừa tạo, lấy URL HTTPS hoặc SSH. Thay `TEN_CUA_BAN` và `TEN_REPO` bằng thông tin thật:

```sh
git remote add origin https://github.com/TEN_CUA_BAN/TEN_REPO.git
git push -u origin main
```

Đăng nhập/xác thực GitHub theo cách tài khoản của bạn đang dùng. Không đưa token, mật khẩu hoặc `.env` vào Git; `.gitignore` đã loại các file này. Cần giữ `ket_qua/tutorial/intent_model.pt`, `ket_qua/tutorial/intent_metrics.json`, `ket_qua/tutorial/mas_metrics.json` và `ket_qua/assignment/summary.json` vì web đọc chúng khi chạy. Kết quả và dataset trong dự án là dữ liệu mô phỏng.

Nếu repository đã có code hoặc đã có remote, không chạy lại một cách máy móc các lệnh khởi tạo trên. Kiểm tra `git status` và `git remote -v`, rồi đồng bộ với lịch sử hiện có trước khi push. Không force-push khi chưa rõ lịch sử.

## 2. Deploy lên Render bằng giao diện

1. Đăng nhập [Render Dashboard](https://dashboard.render.com/) bằng tài khoản của bạn.
2. Chọn **New → Web Service**.
3. Kết nối GitHub nếu cần, cấp quyền cho repository, sau đó chọn repository của dự án.
4. Nếu `du_an_agent02` chính là gốc repository, để **Root Directory** trống. Nếu bạn đẩy nguyên một repository lớn hơn, đặt Root Directory là đường dẫn từ gốc repository đến thư mục này, ví dụ `ASIGNMENT-AGENT_02/du_an_agent02`.
5. Chọn **Language/Runtime: Python 3**, branch muốn deploy và cấu hình:

| Trường | Giá trị |
|---|---|
| Build Command | `pip install -r requirements-render.txt` |
| Start Command | `python code_web/server.py --host 0.0.0.0` |
| Environment variable | `PYTHON_VERSION=3.11.11` |
| Health Check Path (nếu cấu hình) | `/api/overview` |
| Instance type | `Free` nếu bạn muốn thử gói miễn phí và gói có sẵn |

6. Bấm **Create Web Service** / **Deploy Web Service**. Theo dõi Build Logs và Deploy Logs. Khi deploy thành công, mở URL `https://...onrender.com` mà Render cung cấp.
7. Trên website, thử tìm `portable` với ngân sách `100`, thử kịch bản `Dữ liệu kho đã cũ`, và thử phân loại ý định `tìm mua laptop cho tôi`. Xem Logs nếu có lỗi.

Render tự cung cấp biến `PORT`; `server.py` đọc biến đó và Start Command cho phép kết nối trên `0.0.0.0`. `requirements-render.txt` chỉ cài NumPy và PyTorch CPU cho web; notebook và thí nghiệm vẫn dùng `requirements.txt` đầy đủ.

## 3. Tùy chọn: tạo bằng Blueprint

Trong Render, chọn **New → Blueprint**, kết nối repository rồi chọn tệp `render.yaml` ở gốc repository. Tệp này định nghĩa Web Service, Free plan, Python, build/start command và health check. Sau khi review cấu hình và tạo, Render sẽ build/deploy. Tên service có thể cần thay trong `render.yaml` nếu xung đột với tài nguyên hiện có.

## 4. Cập nhật code

Sau khi sửa code tại máy, kiểm tra rồi commit và push lên cùng branch:

```sh
git status
git add .
git commit -m "Update Agent 02 web"
git push
```

Nếu auto-deploy được bật cho service và branch kết nối, Render sẽ build/deploy phiên bản mới khi nhận push. Kiểm tra trạng thái trong tab Deploys; không coi push thành công là deploy thành công.

## 5. Những điểm cần biết khi kiểm tra

- Gói Free đưa web service vào trạng thái nghỉ sau 15 phút không có request; request tiếp theo cần thời gian khởi động lại. Gói này có giới hạn tài nguyên; cài PyTorch CPU có thể mất thời gian, và classifier có thể cần nhiều RAM hơn mức Free cho phép. Nếu thấy lỗi hết bộ nhớ, xem Logs và cân nhắc gói có nhiều RAM hơn.
- Filesystem của Render mặc định không bền qua deploy/restart. Ứng dụng web hiện đọc dữ liệu có sẵn trong repository và không lưu dữ liệu người dùng; nếu sau này thêm upload hoặc train trực tiếp trên server, cần giải pháp lưu trữ bền vững.
- GitHub Pages chỉ chạy nội dung tĩnh. Với website hiện tại, dùng Render **Web Service** để API Python hoạt động.
- Dự án đã chuẩn bị cấu hình và được kiểm tra cục bộ; chưa có repository hoặc service Render của bạn nên chưa thể xác nhận một deployment thực tế.

## Tài liệu tham khảo chính thức

- [Render: Web Services và cấu hình cổng](https://render.com/docs/web-services)
- [Render: thiết lập phiên bản Python](https://render.com/docs/python-version)
- [Render: Free instances](https://render.com/docs/free)
- [Render: Blueprint](https://render.com/docs/infrastructure-as-code)
- [GitHub: đưa code local lên GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [PyTorch: cài phiên bản 2.8.0 CPU](https://pytorch.org/get-started/previous-versions/)
