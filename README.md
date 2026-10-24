# Thực hành buổi 3: Lập trình Python với CoAP

**Sinh viên:** Phạm Khánh Toàn — **Mã sinh viên:** B23DCCN834

Project thực hiện đầy đủ ba bài trong tài liệu thực hành: trao đổi thông điệp, mô phỏng cảm biến, và điều khiển đèn thông minh bằng CoAP Observe.

## Môi trường

- Python 3.10 trở lên (đã kiểm tra cú pháp bằng Python 3.13).
- Thư viện `aiocoap` 0.4.16–0.4.x, khai báo trong `requirements.txt`.
- Giao thức CoAP chạy qua UDP cổng **5683**. Mặc định cả client và server dùng `127.0.0.1`.

Cài đặt:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Trên Linux/macOS, dùng `source .venv/bin/activate` thay cho lệnh kích hoạt PowerShell. Chạy từng lệnh bên dưới trong terminal riêng. Vì cả ba server cùng dùng UDP 5683, hãy **dừng server bài trước** bằng Ctrl+C trước khi chạy server bài tiếp theo.

## Bài 1 — Thông điệp GET/POST

URI: `coap://127.0.0.1:5683/iot/lab/message`

Terminal 1:

```powershell
python bai1/coap_server_bai1.py
```

Terminal 2:

```powershell
python bai1/coap_client_bai1.py --name "Phạm Khánh Toàn" --student-id B23DCCN834
```

Client GET thông điệp chào từ server, rồi POST payload có lời chào, mã sinh viên và họ tên. Server in payload cùng thời điểm nhận và trả `2.04 Changed`. Server lưu thông điệp POST gần nhất; GET sau đó trả về thông điệp ấy. Payload trống hoặc UTF-8 không hợp lệ được trả `4.00 Bad Request`.

## Bài 2 — Cảm biến nhiệt độ/độ ẩm

URI: `coap://127.0.0.1:5683/iot/lab/sensor01/data`

Terminal 1:

```powershell
python bai2/sensor_server_bai2.py
```

Terminal 2:

```powershell
python bai2/monitor_client_bai2.py
```

Server tạo dữ liệu nhiệt độ 20–40 °C và độ ẩm 30–80%, cập nhật mỗi 3 giây. GET trả JSON với `Content-Format: application/json`. Client GET mỗi 3 giây, in thời gian nhận và cảnh báo khi nhiệt độ > 35 °C hoặc độ ẩm < 40%. Nhấn Ctrl+C để dừng; dùng `--count 2` nếu muốn chạy đúng hai lượt.

## Bài 3 — Đèn thông minh và Observe

URI: `coap://127.0.0.1:5683/iot/lab/light01/status`

Terminal 1:

```powershell
python bai3/light_server_bai3.py
```

Terminal 2, mở trước khi thay đổi trạng thái để xem thông báo:

```powershell
python bai3/light_monitor_bai3.py
```

Terminal 3:

```powershell
python bai3/light_controller_bai3.py
```

Nhập `ON`, `OFF`, `STATUS` hoặc `EXIT` trong controller. Trạng thái ban đầu là `OFF`. GET và thông báo Observe trả JSON `{"device_id": "light01", "status": "ON"}` (hoặc `OFF`). PUT gửi `{"device_id": "light01", "command": "ON"}` (hoặc `OFF`). Server trả `2.04 Changed` cho lệnh hợp lệ và chỉ thông báo Observe khi trạng thái thực sự thay đổi. Lệnh hoặc mã thiết bị sai trả `4.00 Bad Request`. Monitor dùng đăng ký Observe và nhận push notification; không dùng GET định kỳ.

## Khi chạy trên máy khác

Chạy server với `--host` là địa chỉ IP của máy server (trên một số transport của Windows, không thể bind vào `0.0.0.0`). Sau đó thay `127.0.0.1` trong URI bằng IP đó qua tham số `--uri` của client, ví dụ:

```powershell
python bai2/sensor_server_bai2.py --host 192.168.1.10
python bai2/monitor_client_bai2.py --uri coap://192.168.1.10:5683/iot/lab/sensor01/data
```

Cho phép UDP cổng 5683 trên tường lửa máy server. Client báo lỗi hoặc timeout khi server không phản hồi.

## Kết quả và minh chứng

| Bài | Kết quả cần quan sát |
| --- | --- |
| 1 | GET trả `2.05 Content`; POST trả `2.04 Changed`, server ghi payload và thời gian nhận. |
| 2 | GET trả JSON đúng định dạng; client in dữ liệu mỗi 3 giây và cảnh báo theo ngưỡng. |
| 3 | GET trả trạng thái; PUT đổi trạng thái; monitor nhận trạng thái đầu và thông báo tự động khi đổi. |

Log chạy thử thực tế được lưu trong [`evidence/`](evidence/):

- [`bai1_client.log`](evidence/bai1_client.log), [`bai1_server.log`](evidence/bai1_server.log): GET và POST kèm thông tin sinh viên.
- [`bai2_client.log`](evidence/bai2_client.log), [`bai2_server.log`](evidence/bai2_server.log): hai lần GET cách nhau 3 giây và một lần cảnh báo nhiệt độ cao.
- [`bai3_controller.log`](evidence/bai3_controller.log), [`bai3_monitor.log`](evidence/bai3_monitor.log), [`bai3_server.log`](evidence/bai3_server.log): trạng thái đầu, bật và tắt đèn qua Observe.
- [`integration_tests.log`](evidence/integration_tests.log): ba kiểm tra CoAP/UDP, gồm hai client Observe đồng thời.

Chạy lại kiểm tra tích hợp sau khi cài thư viện:

```powershell
python -m unittest discover -s tests -v
```

## Cấu trúc

```text
.
├── bai1/
│   ├── coap_server_bai1.py
│   └── coap_client_bai1.py
├── bai2/
│   ├── sensor_server_bai2.py
│   └── monitor_client_bai2.py
├── bai3/
│   ├── light_server_bai3.py
│   ├── light_controller_bai3.py
│   └── light_monitor_bai3.py
├── evidence/
├── requirements.txt
└── README.md
```
