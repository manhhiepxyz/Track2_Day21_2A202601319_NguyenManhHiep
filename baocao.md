# Báo Cáo Thực Hành Lab MLOps

## 1. Kết quả chọn lựa Siêu tham số (Bước 1)
Trong quá trình thực nghiệm tại Bước 1, em đã tiến hành dò tìm và thử nghiệm nhiều tổ hợp siêu tham số khác nhau cho mô hình RandomForestClassifier bằng thư viện MLflow.

**Bộ siêu tham số được chọn cuối cùng:**
- `n_estimators`: 100
- `max_depth`: 20
- `min_samples_split`: 2

**Lý do lựa chọn:**
- Bộ tham số này giúp mô hình đạt được sự cân bằng tốt nhất giữa độ chính xác (Accuracy: ~0.684 ở pha 1 và ~0.758 ở pha 2) và F1-Score (~0.683 và ~0.757) trên tập đánh giá (eval.csv).
- Mức `max_depth=20` đủ sâu để mô hình học được các đặc trưng phức tạp của dữ liệu rượu vang (Wine Quality) gồm 12 đặc trưng, nhưng kết hợp với `min_samples_split=2` và `n_estimators=100` giúp mô hình hội tụ tốt mà không rơi vào trạng thái quá khớp (overfitting).

## 2. Khó khăn gặp phải và cách giải quyết
Trong quá trình triển khai hệ thống CI/CD và kết nối với các dịch vụ Cloud, em đã gặp một số khó khăn kỹ thuật và đã giải quyết như sau:

**Khó khăn 1: Lỗi xác thực AWS (SignatureDoesNotMatch & NoCredentialsError)**
- **Vấn đề:** Khi GitHub Actions và service `mlops-serve` trên máy ảo (EC2) cố gắng kết nối tới S3 để tải model, hệ thống báo lỗi 403 Forbidden hoặc SignatureDoesNotMatch.
- **Cách giải quyết:** Nguyên nhân do trong quá trình copy/paste mã Secret Access Key của AWS bị dư khoảng trắng hoặc ký tự ẩn. Em đã tạo lại cặp Access Key/Secret Key mới trên AWS IAM, sau đó cập nhật cẩn thận vào GitHub Secrets (`CLOUD_CREDENTIALS`) và sửa lại trực tiếp file cấu hình `/etc/systemd/system/mlops-serve.service` trên máy ảo EC2 thông qua SSH. Sau khi reload systemd, mô hình đã kết nối được tới S3.

**Khó khăn 2: Lỗi file cấu hình DVC trên môi trường Linux**
- **Vấn đề:** Ở bước 2, lệnh `dvc pull` trên GitHub Actions (môi trường Ubuntu) báo lỗi không tìm thấy remote.
- **Cách giải quyết:** Do lệnh tạo remote chạy trên Windows PowerShell đã tự động bọc tên remote bằng cặp dấu nháy đơn trong file `.dvc/config` (thành `['remote "s3remote"']`). Em đã mở file này ra, xóa các dấu nháy đơn bị thừa thành chuẩn INI (`[remote "s3remote"]`), sau đó commit và push lại lên GitHub. Lỗi đã được khắc phục hoàn toàn.

**Khó khăn 3: Service API (FastAPI) sập lúc khởi động trên EC2**
- **Vấn đề:** Mặc dù code pipeline chạy qua bước Deploy, nhưng lệnh test bằng `curl` luôn bị lỗi `Connection refused` hoặc `Method Not Allowed`.
- **Cách giải quyết:** Kiểm tra `journalctl` trên EC2 phát hiện service bị crash do lỗi credentials S3 (đã nêu ở khó khăn 1). Sau khi cập nhật lại đúng key mới cho file `.service` trên EC2, service đã hoạt động ổn định ở port 8000. Lỗi `Method Not Allowed` khi test do gọi `curl` mặc định (GET) thay vì `POST` kèm JSON data; em đã đổi sang lệnh chuẩn `curl -X POST ... -d '{"features": [...]}'` (hoặc `Invoke-RestMethod` với tham số Post trên PowerShell) và đã nhận được kết quả dự đoán (VD: `{"prediction":0,"label":"thap"}`).
