from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from functools import wraps
import sys
import os
import io
import re
import openpyxl
from datetime import datetime

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))
from db import (
    init_db, get_db_connection, search_serials, search_esd, 
    get_statistics, verify_admin_login, import_bulk_licenses,
    search_by_contract, get_contracts_summary, delete_licenses_by_contract
)
from seed_data import seed_database

app = Flask(__name__)
app.secret_key = "hqn_software_microsoft_portal_secret_key_2026"

# Ensure DB is created on launch
init_db()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/portal/home')
def home():
    return render_template('home.html', active_page='home')


@app.route('/portal/search/serial', methods=['GET'])
def search_serial_page():
    return render_template('search_serial.html', active_page='serial')


@app.route('/portal/api/search/serial', methods=['POST'])
def api_search_serial():
    data = request.get_json(silent=True) or {}
    query_value = data.get('value', '').strip()
    if not query_value:
        return jsonify({"error": "Vui lòng nhập ít nhất một số seri.", "rows": []})

    rows = search_serials(query_value)
    return jsonify({"error": "", "rows": rows})


@app.route('/portal/search/esd', methods=['GET'])
def search_esd_page():
    return render_template('search_esd.html', active_page='esd')


@app.route('/portal/api/search/esd', methods=['POST'])
def api_search_esd():
    data = request.get_json(silent=True) or {}
    query_value = data.get('value', '').strip()
    if not query_value:
        return jsonify({"error": "Vui lòng nhập ít nhất một số ESD hoặc mã giao dịch.", "rows": []})

    rows = search_esd(query_value)
    return jsonify({"error": "", "rows": rows})


# Admin Authentication Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        if session.get('admin_logged_in'):
            return redirect(url_for('admin_page'))
        return render_template('admin_login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    user = verify_admin_login(username, password)
    if user:
        session['admin_logged_in'] = True
        session['admin_user'] = user['username']
        session['admin_full_name'] = user['full_name']
        return redirect(url_for('admin_page'))
    else:
        return render_template('admin_login.html', error="Tên đăng nhập hoặc mật khẩu không chính xác.")


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


# Protected Admin Routes
@app.route('/admin')
@admin_required
def admin_page():
    stats = get_statistics()
    contracts_summary = get_contracts_summary()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM physical_licenses ORDER BY id DESC")
    physical_list = cursor.fetchall()

    cursor.execute("SELECT * FROM esd_licenses ORDER BY id DESC")
    esd_list = cursor.fetchall()
    conn.close()

    message = request.args.get('message')
    error = request.args.get('error')

    return render_template(
        'admin.html',
        active_page='admin',
        physical_list=physical_list,
        esd_list=esd_list,
        stats=stats,
        contracts_summary=contracts_summary,
        message=message,
        error=error
    )


@app.route('/admin/add/physical', methods=['POST'])
@admin_required
def admin_add_physical():
    serial_number = request.form.get('serial_number', '').strip()
    product_code = request.form.get('product_code', '').strip()
    name_vn = request.form.get('name_vn', '').strip()
    name_en = request.form.get('name_en', '').strip()
    country_name = request.form.get('country_name', '').strip() or 'Singapore'
    distribute_date = request.form.get('distribute_date', '').strip()
    customer_or_reseller = request.form.get('customer_or_reseller', '').strip()
    notes = request.form.get('notes', '').strip()

    if not serial_number or not product_code or not name_vn:
        return redirect(url_for('admin_page', error="Vui lòng điền đầy đủ các thông tin bắt buộc."))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO physical_licenses 
            (serial_number, product_code, name_en, name_vn, country_name, status, distributor, distribute_date, customer_or_reseller, notes)
            VALUES (?, ?, ?, ?, ?, 'Chính hãng HQN Software', 'HQN Software', ?, ?, ?)
        """, (serial_number, product_code, name_en, name_vn, country_name, distribute_date, customer_or_reseller, notes))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_page', message=f"Đã thêm thành công số Seri {serial_number}."))
    except Exception as e:
        return redirect(url_for('admin_page', error=f"Lỗi: Số Seri có thể đã tồn tại ({e})."))


@app.route('/admin/delete/physical/<int:item_id>', methods=['POST'])
@admin_required
def admin_delete_physical(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM physical_licenses WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_page', message=f"Đã xóa bản ghi ID {item_id}."))


@app.route('/admin/add/esd', methods=['POST'])
@admin_required
def admin_add_esd():
    esd_key = request.form.get('esd_key', '').strip()
    transaction_code = request.form.get('transaction_code', '').strip()
    product_code = request.form.get('product_code', '').strip()
    name_vn = request.form.get('name_vn', '').strip()
    name_en = request.form.get('name_en', '').strip()
    transaction_date = request.form.get('transaction_date', '').strip()
    reseller_name = request.form.get('reseller_name', '').strip() or 'Đại lý ủy quyền HQN Software'
    customer_email = request.form.get('customer_email', '').strip()
    notes = request.form.get('notes', '').strip()

    if not esd_key or not transaction_code or not product_code:
        return redirect(url_for('admin_page', error="Vui lòng điền đầy đủ các thông tin bắt buộc."))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO esd_licenses 
            (esd_key, transaction_code, product_code, name_en, name_vn, transaction_date, status, reseller_name, customer_email, notes)
            VALUES (?, ?, ?, ?, ?, ?, 'Đã cấp hợp lệ', ?, ?, ?)
        """, (esd_key, transaction_code, product_code, name_en, name_vn, transaction_date, reseller_name, customer_email, notes))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_page', message=f"Đã thêm thành công Key ESD {esd_key}."))
    except Exception as e:
        return redirect(url_for('admin_page', error=f"Lỗi: Mã Key hoặc Mã Giao Dịch có thể đã tồn tại ({e})."))


@app.route('/admin/delete/esd/<int:item_id>', methods=['POST'])
@admin_required
def admin_delete_esd(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM esd_licenses WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_page', message=f"Đã xóa bản ghi ID {item_id}."))


@app.route('/admin/delete/contract', methods=['POST'])
@admin_required
def admin_delete_contract():
    transaction_code = request.form.get('transaction_code', '').strip()
    if not transaction_code:
        return redirect(url_for('admin_page', error="Vui lòng nhập hoặc chọn mã hợp đồng / mã giao dịch cần xóa."))

    res = delete_licenses_by_contract(transaction_code)
    if res['success']:
        msg = f"Đã xóa thành công toàn bộ {res['total_deleted']} key thuộc hợp đồng / giao dịch '{transaction_code}'."
        return redirect(url_for('admin_page', message=msg))
    else:
        return redirect(url_for('admin_page', error=f"Không tìm thấy bản ghi nào thuộc mã hợp đồng / giao dịch '{transaction_code}'."))


PRODUCT_KEY_RE = re.compile(
    r'[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}',
    re.IGNORECASE
)

SKIP_TOKENS = {
    'key', 'product key', 'serial', 's/n', 'stt', 'id',
    'mã key', 'bản quyền', 'mã_key_bản_quyền', 'license key',
    'license', 'danh sách', 'code', 'product'
}


def parse_keys_smart(text):
    """Extract product keys from arbitrary text using regex first, then token fallback."""
    # Primary: regex for standard 25-char Microsoft product key format
    found = PRODUCT_KEY_RE.findall(text)
    if found:
        seen = set()
        keys = []
        for k in found:
            ku = k.upper().strip()
            if ku not in seen:
                seen.add(ku)
                keys.append(ku)
        return keys
    # Fallback: token splitter for serial numbers / short codes
    tokens = re.split(r'[,;\t\r\n ]+', text)
    keys = []
    seen = set()
    for t in tokens:
        c = t.strip().upper()
        if c and c.lower() not in SKIP_TOKENS and len(c) >= 4 and c not in seen:
            seen.add(c)
            keys.append(c)
    return keys


def extract_keys_from_excel(file_storage):
    """Read all cells from all sheets and extract product keys via smart parser."""
    filename = file_storage.filename.lower()
    all_text = ""

    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        wb = openpyxl.load_workbook(file_storage, data_only=True)
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if cell is not None:
                        all_text += " " + str(cell)
    elif filename.endswith('.csv') or filename.endswith('.txt'):
        all_text = file_storage.read().decode('utf-8', errors='ignore')

    return parse_keys_smart(all_text)


@app.route('/admin/sample-excel')
@admin_required
def admin_sample_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh_Sach_Key"
    
    # Headers and sample keys
    ws['A1'] = "Mã_Key_Bản_Quyền"
    ws.column_dimensions['A'].width = 38
    
    samples = [
        "VK7JG-NPHTM-C97JM-9MPGT-3V66T",
        "W269N-WFGWX-YVC9B-4J6C9-T83GX",
        "B7Q2P-K8NYM-Q3TWC-94X2R-V8HMF",
        "D9KP4-82NCV-TR77X-B2YWM-GQ92M",
        "7H2NM-CY4X8-P3B9K-RT8VD-M4QX2",
        "SN-W11P-98214501",
        "SN-OFF24-7712903"
    ]
    for idx, key in enumerate(samples, start=2):
        ws[f'A{idx}'] = key

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name="mau_import_key.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route('/admin/import/bulk', methods=['POST'])
@admin_required
def admin_import_bulk():
    license_type = request.form.get('license_type', 'esd').strip()
    product_code = request.form.get('product_code', '').strip()
    name_vn = request.form.get('name_vn', '').strip()
    name_en = request.form.get('name_en', '').strip()
    transaction_code = request.form.get('transaction_code', '').strip()
    end_user = request.form.get('end_user', '').strip()
    customer_email = request.form.get('customer_email', '').strip()
    transaction_date = request.form.get('transaction_date', '').strip()
    country_name = request.form.get('country_name', '').strip() or 'Singapore'
    notes = request.form.get('notes', '').strip()
    
    if not product_code or not name_vn:
        return redirect(url_for('admin_page', error="Vui lòng nhập đầy đủ Mã Part và Tên sản phẩm tiếng Việt."))

    if not transaction_date:
        transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if license_type == 'esd' and not transaction_code:
        transaction_code = f"HQN-ESD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Extract keys from uploaded file or textarea
    keys = []
    excel_file = request.files.get('excel_file')
    if excel_file and excel_file.filename:
        keys.extend(extract_keys_from_excel(excel_file))
        
    pasted_keys = request.form.get('pasted_keys', '').strip()
    if pasted_keys:
        keys.extend(parse_keys_smart(pasted_keys))

    if not keys:
        return redirect(url_for('admin_page', error="Không tìm thấy key nào từ file Excel tải lên hoặc vùng dán danh sách key."))

    res = import_bulk_licenses(
        license_type=license_type,
        keys=keys,
        product_code=product_code,
        name_vn=name_vn,
        name_en=name_en,
        transaction_code=transaction_code,
        end_user=end_user,
        customer_email=customer_email,
        transaction_date=transaction_date,
        country_name=country_name,
        distributor="HQN Software",
        reseller_name="HQN Software",
        notes=notes
    )

    msg = f"Đã import thành công {res['imported_count']} key cho khách hàng '{end_user or 'Doanh nghiệp'}'. (Bỏ qua {res['skipped_count']} key đã có sẵn trong tổng số {res['total']} key)."
    return redirect(url_for('admin_page', message=msg))


@app.route('/admin/reseed', methods=['POST'])
@admin_required
def admin_reseed():
    seed_database()
    return redirect(url_for('admin_page', message="Đã khôi phục dữ liệu mẫu gốc ban đầu thành công."))


@app.route('/portal/search/contract', methods=['GET'])
def search_contract_page():
    """Page: Search keys by contract/transaction code (masked output)."""
    return render_template('search_contract.html')


@app.route('/portal/api/search/contract', methods=['POST'])
def api_search_contract():
    """API: Return masked keys for a given transaction/contract code."""
    transaction_code = request.form.get('transaction_code', '').strip()
    if not transaction_code:
        return render_template('search_contract.html', error="Vui lòng nhập mã hợp đồng / mã giao dịch.")
    result = search_by_contract(transaction_code)
    return render_template('search_contract.html', result=result, query=transaction_code)


if __name__ == '__main__':
    # Run on port 5000
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Microsoft HQN Software License Portal on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
