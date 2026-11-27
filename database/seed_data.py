import os
import sqlite3
from db import get_db_connection, init_db

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sample Physical Licenses (Key vật lý - tra cứu bằng số Seri / S/N)
    physical_items = [
        (
            "SN-W11P-98214501",
            "FQC-10528",
            "Windows 11 Pro 64Bit Eng Intl 1pk DSP OEI DVD",
            "Phần mềm Windows 11 Pro 64-bit bản quyền OEM (Bản đĩa/thẻ cào)",
            "Singapore",
            "Chính hãng HQN Software",
            "HQN Software",
            "2024-01-10",
            "2024-02-15",
            "Đại lý Phong Vũ Computer",
            "Key vật lý nguyên seal, tem bảo đảm chính hãng HQN Software"
        ),
        (
            "SN-W11P-98214502",
            "FQC-10528",
            "Windows 11 Pro 64Bit Eng Intl 1pk DSP OEI DVD",
            "Phần mềm Windows 11 Pro 64-bit bản quyền OEM",
            "Singapore",
            "Chính hãng HQN Software",
            "HQN Software",
            "2024-01-10",
            "2024-03-20",
            "Công ty TNHH Tin Học Mai Hoàng",
            "Kiểm tra tem hợp lệ"
        ),
        (
            "SN-W11H-84729110",
            "KW9-00632",
            "Windows 11 Home 64Bit Eng Intl 1pk DSP OEI DVD",
            "Phần mềm Windows 11 Home 64-bit bản quyền OEM",
            "Singapore",
            "Chính hãng HQN Software",
            "HQN Software",
            "2024-02-05",
            "2024-03-12",
            "Hệ thống FPT Shop",
            "Phân phối qua FPT Retail"
        ),
        (
            "SN-OFF24-7712903",
            "HAV-00163",
            "Office Home & Business 2024 English APAC EM Medialess",
            "Phần mềm Microsoft Office Home and Business 2024 All Lng (Thẻ bản quyền)",
            "Ireland",
            "Chính hãng HQN Software",
            "HQN Software",
            "2024-10-02",
            "2024-10-25",
            "Đại lý CellphoneS",
            "Bản quyền vĩnh viễn cho 1 PC/Mac"
        ),
        (
            "SN-OFF21-5541982",
            "T5D-03485",
            "Office Home and Business 2021 All Lng APAC EM Medialess",
            "Phần mềm Microsoft Office Home and Business 2021 All Lng",
            "Ireland",
            "Chính hãng HQN Software",
            "HQN Software",
            "2023-11-15",
            "2023-12-01",
            "Công ty Cổ phần Thế Giới Di Động",
            "Bản quyền chính hãng HQN Software"
        ),
        (
            "SN-OFS21-3321876",
            "79G-05337",
            "Office Home and Student 2021 All Lng APAC EM Medialess",
            "Phần mềm Microsoft Office Home & Student 2021",
            "Singapore",
            "Chính hãng HQN Software",
            "HQN Software",
            "2023-09-18",
            "2023-10-05",
            "Hệ thống GearVN",
            "Dành cho học sinh - sinh viên và gia đình"
        ),
        (
            "SN-SRV22-1092834",
            "P73-08328",
            "Windows Server 2022 Standard 16 Core English OEI DVD",
            "Phần mềm Windows Server 2022 Standard 16 Core",
            "United States",
            "Chính hãng HQN Software",
            "HQN Software",
            "2024-04-10",
            "2024-05-18",
            "Doanh nghiệp CMC Telecom",
            "Cấp cho dự án Server Data Center"
        ),
        (
            "SN-W10P-6619280",
            "FQC-08929",
            "Windows 10 Pro 64Bit Eng Intl 1pk DSP OEI DVD",
            "Phần mềm Windows 10 Pro 64-bit bản quyền OEM",
            "Ireland",
            "Chính hãng HQN Software",
            "HQN Software",
            "2023-05-12",
            "2023-06-01",
            "Đại lý Hà Nội Computer (Hacom)",
            "Bản quyền kích hoạt OEM"
        ),
        (
            "SN001",
            "FQC-10528",
            "Windows 11 Pro 64Bit Eng Intl 1pk DSP OEI DVD",
            "Phần mềm Windows 11 Pro 64-bit bản quyền OEM",
            "Singapore",
            "Chính hãng HQN Software",
            "HQN Software",
            "2024-01-01",
            "2024-01-15",
            "Đại lý Minh Thông",
            "Mã test mẫu chuẩn SN001"
        ),
        (
            "SN002",
            "HAV-00163",
            "Office Home & Business 2024 English APAC EM Medialess",
            "Phần mềm Microsoft Office Home and Business 2024",
            "Ireland",
            "Chính hãng HQN Software",
            "HQN Software",
            "2024-01-01",
            "2024-01-15",
            "Đại lý Viettel Store",
            "Mã test mẫu chuẩn SN002"
        )
    ]

    for item in physical_items:
        cursor.execute("""
            INSERT OR REPLACE INTO physical_licenses 
            (serial_number, product_code, name_en, name_vn, country_name, status, distributor, import_date, distribute_date, customer_or_reseller, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)

    # Sample Electronic ESD Licenses (Key điện tử - tra cứu bằng Product Key 25 ký tự hoặc Mã giao dịch)
    esd_items = [
        (
            "VK7JG-NPHTM-C97JM-9MPGT-3V66T",
            "HQN-ESD-TX88910",
            "FQC-10572",
            "Windows 11 Professional ESD 32-bit/64-bit All Lng",
            "Bản quyền Windows 11 Pro điện tử (ESD Online License)",
            "2024-09-12 10:24:18",
            "Đã cấp hợp lệ",
            "Đại lý FPT Retail ESD Portal",
            "khachhang.it@company.vn",
            "Key phân phối trực tiếp qua hệ thống ESD HQN Software"
        ),
        (
            "W269N-WFGWX-YVC9B-4J6C9-T83GX",
            "HQN-ESD-TX92341",
            "FQC-10572",
            "Windows 11 Professional ESD 32-bit/64-bit All Lng",
            "Bản quyền Windows 11 Pro điện tử (ESD Online License)",
            "2024-10-05 14:15:30",
            "Đã cấp hợp lệ",
            "Phong Vũ Online Store",
            "admin@nguyenkim.com",
            "Xác thực qua chứng thư số ESD HQN"
        ),
        (
            "NMMKJ-6RK4F-KMJVX-8D9MJ-6MWKP",
            "HQN-ESD-TX93452",
            "KW9-00664",
            "Windows 11 Home ESD 32-bit/64-bit All Lng",
            "Bản quyền Windows 11 Home điện tử (ESD Online License)",
            "2024-10-18 09:40:11",
            "Đã cấp hợp lệ",
            "CellphoneS Smartshop",
            "user24@gmail.com",
            "Key điện tử chính hãng kích hoạt trên trang setup.office.com hoặc Windows Settings"
        ),
        (
            "B7Q2P-K8NYM-Q3TWC-94X2R-V8HMF",
            "HQN-ESD-TX94108",
            "HAV-00200",
            "Office Home and Business 2024 All Lng ESD",
            "Bản quyền Microsoft Office Home and Business 2024 điện tử (ESD)",
            "2024-11-01 16:02:45",
            "Đã cấp hợp lệ",
            "Hacom Computer ESD",
            "finance@vinacorp.vn",
            "Bản quyền vĩnh viễn Office 2024, tích hợp Outlook, Word, Excel, PowerPoint"
        ),
        (
            "7H2NM-CY4X8-P3B9K-RT8VD-M4QX2",
            "HQN-ESD-TX85412",
            "T5D-03511",
            "Office Home and Business 2021 All Lng ESD",
            "Bản quyền Microsoft Office Home and Business 2021 điện tử (ESD)",
            "2024-08-20 11:10:05",
            "Đã cấp hợp lệ",
            "Viettel Solutions",
            "contact@techasia.vn",
            "Bản quyền kích hoạt online qua Microsoft Account"
        ),
        (
            "D9KP4-82NCV-TR77X-B2YWM-GQ92M",
            "HQN-ESD-TX89923",
            "KLQ-00645",
            "Microsoft 365 Business Standard 1 Year ESD Sub",
            "Bản quyền Microsoft 365 Doanh nghiệp Tiêu chuẩn (Gói 1 năm điện tử)",
            "2024-10-22 08:30:00",
            "Đã cấp hợp lệ",
            "Thế Giới Di Động ESD",
            "director@startupviet.com",
            "Bao gồm bộ ứng dụng Office cao cấp + 1TB OneDrive + Teams Doanh nghiệp"
        ),
        (
            "3X8MN-9K42T-VCP3Q-R84DY-2MB7W",
            "HQN-ESD-TX81190",
            "6GQ-01157",
            "Microsoft 365 Family 32/64-bit All Lng Sub 1YR ESD",
            "Bản quyền Microsoft 365 Family (Gia đình 6 người - 1 năm)",
            "2024-07-15 15:45:22",
            "Đã cấp hợp lệ",
            "Đại lý Phúc Anh Smart World",
            "family.office@gmail.com",
            "Key ESD điện tử cấp qua email"
        ),
        (
            "ESD001",
            "HQN-ESD-TX00001",
            "FQC-10572",
            "Windows 11 Professional ESD 32-bit/64-bit All Lng",
            "Bản quyền Windows 11 Pro điện tử ESD",
            "2024-01-01 09:00:00",
            "Đã cấp hợp lệ",
            "Cổng phân phối điện tử HQN Software",
            "demo1@hqnsoftware.com",
            "Mã test mẫu chuẩn ESD001"
        ),
        (
            "ESD002",
            "HQN-ESD-TX00002",
            "HAV-00200",
            "Office Home and Business 2024 All Lng ESD",
            "Bản quyền Microsoft Office Home and Business 2024 điện tử (ESD)",
            "2024-01-02 14:00:00",
            "Đã cấp hợp lệ",
            "Cổng phân phối điện tử HQN Software",
            "demo2@hqnsoftware.com",
            "Mã test mẫu chuẩn ESD002"
        )
    ]

    for item in esd_items:
        cursor.execute("""
            INSERT OR REPLACE INTO esd_licenses
            (esd_key, transaction_code, product_code, name_en, name_vn, transaction_date, status, reseller_name, customer_email, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)

    conn.commit()
    conn.close()
    print("Database seeded successfully with HQN Software license records.")

if __name__ == "__main__":
    seed_database()
