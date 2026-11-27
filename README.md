# Hệ Thống Cổng Tra Cứu Bản Quyền Microsoft - HQN Software

Dự án này là website tra cứu, xác thực và quản lý key bản quyền phần mềm Microsoft (Windows 11 Pro, Office 2024, Microsoft 365, Windows Server...), được xây dựng với giao diện chuyên nghiệp, hiện đại và cơ sở dữ liệu riêng biệt.

---

## 1. Tính Năng Chính

- **Giao diện người dùng công khai (Public Portal):**
  - Tông màu xanh Navy (`#0b1b33`, `#0f2743`) kết hợp xanh Microsoft Blue (`#0078d4`) và bảng dữ liệu chuyên nghiệp (`#0f766e`).
  - Toàn bộ thương hiệu đã chuyển sang **HQN Software** kèm biểu trưng `logo.png`.
  - **Không chứa bất kỳ nút bấm quản trị hay chức năng quản lý hệ thống trên trang chủ**, đảm bảo tính bảo mật và trải nghiệm tra cứu riêng biệt cho khách hàng.
  
- **2 Phương thức tra cứu bản quyền:**
  1. **Tra cứu số Seri (Key vật lý - `/portal/search/serial`):** Dành cho bản quyền đóng gói COA / Hộp đĩa DVD / Thẻ cào. Nhập danh sách số Seri (S/N) phân tách bằng dấu phẩy hoặc xuống dòng để kiểm tra xuất xứ, tính chính hãng từ HQN Software, xem chứng nhận bản quyền và xuất file CSV.
  2. **Tra cứu số ESD (Key điện tử - `/portal/search/esd`):** Dành cho bản quyền điện tử. Hỗ trợ tra cứu bằng Product Key 25 ký tự hoặc Mã giao dịch ESD (`HQN-ESD-TX...`).

- **Thông tin liên hệ chính thức:**
  - **Số điện thoại:** `0913.370.239`
  - **Email:** `hqngroup@gmail.com`
  - **Địa chỉ:** `NO04-LK192 Khu LK27-28, P. Dương Nội, Hà Nội`

- **Trang Quản trị Hệ Thống Riêng Biệt (`/admin`):**
  - **Bảo mật đăng nhập:** Truy cập `/admin` bắt buộc phải đăng nhập tài khoản quản trị viên.
  - **Tài khoản mặc định:**
    - Tên đăng nhập: `admin`
    - Mật khẩu: `admin123`
  - **Chức năng quản trị:**
    - **Import Lô Key Doanh Nghiệp (Excel / Dán trực tiếp):** Nhập hàng loạt hàng trăm/hàng nghìn key từ bảng Excel (chỉ cần chứa 1 cột key) hoặc dán trực tiếp từ clipboard, đồng thời điền thủ công các thông tin chung của hợp đồng (Tên sản phẩm, Mã part, Tên Doanh nghiệp sử dụng - End-User, Mã giao dịch, Email nhận key...). Hệ thống tự động lọc trùng và nạp nhanh vào cơ sở dữ liệu.
    - **Tải file Excel mẫu:** Có nút tải tệp `mau_import_key.xlsx` chuẩn để thao tác nhanh.
    - **Quản lý danh sách:** Thêm đơn lẻ, xóa, tìm kiếm danh sách số Seri vật lý & Key ESD điện tử, khôi phục dữ liệu gốc, nút đăng xuất an toàn.

---

## 2. Cấu Trúc Dự Án

```
d:\Project Antigravity\microsoft\
├── app.py                     # Ứng dụng Web Flask chính & REST API + Bảo mật Admin
├── test_app.py                # Kịch bản kiểm thử tự động
├── README.md                  # Tài liệu hướng dẫn sử dụng
├── logo.png                   # Logo chính thức của HQN Software
├── database/
│   ├── db.py                  # Khởi tạo SQLite, xác thực tài khoản, tra cứu & thống kê
│   ├── seed_data.py           # Dữ liệu mẫu ban đầu cho Key vật lý & ESD
│   └── license_portal.db      # Tệp cơ sở dữ liệu SQLite độc lập
├── static/
│   ├── css/
│   │   └── portal.css         # Bộ stylesheet giao diện
│   └── img/
│       ├── logo.png           # Logo HQN Software
│       ├── microsoft_logo.png # Logo Microsoft
│       ├── ban_quyen.webp     # Banner nhận diện bản quyền chính hãng
│       └── Group_4.jpg        # Banner hướng dẫn tra cứu
└── templates/
    ├── base.html              # Layout chung
    ├── home.html              # Trang chủ tra cứu (đã bỏ mọi nút quản trị)
    ├── search_serial.html     # Giao diện tra cứu số Seri (Key vật lý)
    ├── search_esd.html        # Giao diện tra cứu số ESD (Key điện tử)
    ├── admin_login.html       # Trang đăng nhập tài khoản Quản trị viên
    └── admin.html             # Trang quản trị cơ sở dữ liệu riêng biệt
```

---

## 3. Khởi Chạy Ứng Dụng

Mở PowerShell tại thư mục dự án:
```powershell
python app.py
```

Truy cập:
- **Cổng tra cứu công khai:** [http://localhost:5000/](http://localhost:5000/)
- **Tra cứu số Seri vật lý:** [http://localhost:5000/portal/search/serial](http://localhost:5000/portal/search/serial)
- **Tra cứu Key ESD điện tử:** [http://localhost:5000/portal/search/esd](http://localhost:5000/portal/search/esd)
- **Trang đăng nhập Quản trị:** [http://localhost:5000/admin/login](http://localhost:5000/admin/login)
  *(Tài khoản: `admin` / Mật khẩu: `admin123`)*
