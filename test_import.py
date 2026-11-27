import sys
import io
import time
import openpyxl
from app import app
from database.db import get_db_connection

client = app.test_client()
uid = int(time.time())

print("1. Login as admin...")
with client:
    res = client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert res.status_code == 200
    print("Logged in successfully.")

    print("2. Test downloading sample excel...")
    res_excel = client.get('/admin/sample-excel')
    assert res_excel.status_code == 200
    assert "application/vnd.openxmlformats" in res_excel.headers["Content-Type"]
    wb = openpyxl.load_workbook(io.BytesIO(res_excel.data))
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    assert len(rows) >= 5
    print(f"Sample Excel has {len(rows)} rows, header: {rows[0][0]}")
    print("PASSED: Sample Excel generated correctly.")

    print("3. Test bulk import via Excel file...")
    test_wb = openpyxl.Workbook()
    test_ws = test_wb.active
    test_ws.title = "Keys"
    test_ws.append(["Mã Key Bản Quyền"])
    k1 = f"CORP-KEY-A-{uid}"
    k2 = f"CORP-KEY-B-{uid}"
    k3 = f"CORP-KEY-C-{uid}"
    test_ws.append([k1])
    test_ws.append([k2])
    test_ws.append([k3])
    excel_buf = io.BytesIO()
    test_wb.save(excel_buf)
    excel_buf.seek(0)

    import_data = {
        'license_type': 'esd',
        'product_code': 'FQC-10572',
        'name_vn': 'Bản quyền Windows 11 Pro ESD Doanh Nghiệp',
        'name_en': 'Windows 11 Professional ESD',
        'transaction_code': f'HQN-TX-{uid}',
        'end_user': 'Tập đoàn Viettel - Khối Kỹ Thuật',
        'customer_email': 'it@viettel.vn',
        'transaction_date': '2026-11-19 14:00:00',
        'excel_file': (excel_buf, 'keys_enterprise.xlsx')
    }

    res_import = client.post('/admin/import/bulk', data=import_data, content_type='multipart/form-data', follow_redirects=True)
    assert res_import.status_code == 200
    html = res_import.data.decode('utf-8')
    assert 'Đã import thành công 3 key' in html
    print("PASSED: Bulk import via Excel file succeeded (3 keys).")

    print("4. Verify database records...")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT esd_key, transaction_code, reseller_name FROM esd_licenses WHERE esd_key = ?", (k1,))
    row = c.fetchone()
    assert row is not None
    assert row['transaction_code'] == f'HQN-TX-{uid}'
    print(f"Verified DB record: {row['esd_key']} -> {row['transaction_code']}")
    conn.close()

    print("5. Test bulk import via copy-paste textarea...")
    s1 = f"SN-PASTE-1-{uid}"
    s2 = f"SN-PASTE-2-{uid}"
    paste_data = {
        'license_type': 'physical',
        'product_code': 'FQC-10528',
        'name_vn': 'Windows 11 Pro OEM DVD Doanh Nghiệp',
        'name_en': 'Windows 11 Pro OEM DVD',
        'end_user': 'Công ty FPT Software',
        'pasted_keys': f'{s1}\n{s2}'
    }
    res_paste = client.post('/admin/import/bulk', data=paste_data, follow_redirects=True)
    assert res_paste.status_code == 200
    html2 = res_paste.data.decode('utf-8')
    assert 'Đã import thành công 2 key' in html2
    print("PASSED: Bulk import via copy-paste succeeded (2 keys).")

    print("6. Test duplicate prevention on re-import...")
    res_reimport = client.post('/admin/import/bulk', data=paste_data, follow_redirects=True)
    assert res_reimport.status_code == 200
    html3 = res_reimport.data.decode('utf-8')
    assert 'Bỏ qua 2 key đã có sẵn' in html3
    print("PASSED: Duplicate keys safely skipped.")

print("\nALL BULK IMPORT TEST CASES PASSED SUCCESSFULLY!")
