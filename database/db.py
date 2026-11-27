import sqlite3
import os
from typing import List, Dict, Any, Optional
from werkzeug.security import generate_password_hash, check_password_hash

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "license_portal.db")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for Physical Serial Licenses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS physical_licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial_number TEXT UNIQUE NOT NULL COLLATE NOCASE,
            product_code TEXT NOT NULL,
            name_en TEXT NOT NULL,
            name_vn TEXT NOT NULL,
            country_name TEXT NOT NULL,
            status TEXT DEFAULT 'Chính hãng HQN Software',
            distributor TEXT DEFAULT 'HQN Software',
            import_date TEXT,
            distribute_date TEXT,
            customer_or_reseller TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for Electronic ESD Licenses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS esd_licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            esd_key TEXT UNIQUE NOT NULL COLLATE NOCASE,
            transaction_code TEXT NOT NULL COLLATE NOCASE,
            product_code TEXT NOT NULL,
            name_en TEXT NOT NULL,
            name_vn TEXT NOT NULL,
            transaction_date TEXT NOT NULL,
            status TEXT DEFAULT 'Đã cấp hợp lệ',
            reseller_name TEXT DEFAULT 'Đại lý ủy quyền HQN Software',
            customer_email TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for Search History Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_type TEXT NOT NULL,
            query_value TEXT NOT NULL,
            found_count INTEGER NOT NULL DEFAULT 0,
            ip_address TEXT,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for Admin Accounts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            full_name TEXT DEFAULT 'Quản trị viên HQN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert default admin account if not exists: admin / admin123
    cursor.execute("SELECT id FROM admin_users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("admin123")
        cursor.execute("""
            INSERT INTO admin_users (username, password_hash, full_name)
            VALUES ('admin', ?, 'HQN Software Administrator')
        """, (hashed_pw,))

    conn.commit()
    conn.close()


def verify_admin_login(username: str, password: str) -> Optional[Dict[str, Any]]:
    if not username or not password:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, full_name FROM admin_users WHERE username = ?", (username.strip(),))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user["password_hash"], password):
        return {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"]
        }
    return None


def search_serials(query_string: str) -> List[Dict[str, Any]]:
    """
    Search multiple serial numbers separated by commas, newlines, spaces, or semicolons.
    """
    if not query_string:
        return []

    tokens = [t.strip() for t in query_string.replace(';', ',').replace('\n', ',').replace('\r', '').split(',') if t.strip()]
    if not tokens:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()

    rows = []
    seen = set()

    for idx, token in enumerate(tokens, start=1):
        clean_token = token.upper()
        if clean_token in seen:
            continue
        seen.add(clean_token)

        cursor.execute("""
            SELECT serial_number, product_code, name_en, name_vn, country_name, status, distributor, distribute_date
            FROM physical_licenses
            WHERE UPPER(serial_number) = ?
        """, (clean_token,))
        match = cursor.fetchone()

        if match:
            rows.append({
                "no": len(rows) + 1,
                "lot_name": match["serial_number"],
                "default_code": match["product_code"],
                "name": match["name_en"],
                "vn_name": match["name_vn"],
                "country_name": match["country_name"],
                "status": match["status"] or "Chính hãng HQN Software",
                "distributor": match["distributor"] or "HQN Software",
                "distribute_date": match["distribute_date"],
                "is_valid": True
            })
        else:
            rows.append({
                "no": len(rows) + 1,
                "lot_name": token,
                "default_code": "—",
                "name": "Không tìm thấy trong hệ thống HQN Software",
                "vn_name": "Sản phẩm không thuộc hệ thống phân phối HQN Software hoặc số Seri không tồn tại",
                "country_name": "—",
                "status": "Không hợp lệ / Không tồn tại",
                "distributor": "—",
                "distribute_date": "—",
                "is_valid": False
            })

    valid_count = sum(1 for r in rows if r["is_valid"])
    cursor.execute("""
        INSERT INTO search_logs (search_type, query_value, found_count)
        VALUES ('serial', ?, ?)
    """, (query_string, valid_count))
    conn.commit()
    conn.close()

    return rows


def search_esd(query_string: str) -> List[Dict[str, Any]]:
    """
    Search multiple ESD keys or Transaction codes separated by commas, newlines, spaces, or semicolons.
    """
    if not query_string:
        return []

    tokens = [t.strip() for t in query_string.replace(';', ',').replace('\n', ',').replace('\r', '').split(',') if t.strip()]
    if not tokens:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()

    rows = []
    seen = set()

    for idx, token in enumerate(tokens, start=1):
        clean_token = token.upper()
        if clean_token in seen:
            continue
        seen.add(clean_token)

        cursor.execute("""
            SELECT esd_key, transaction_code, product_code, name_en, name_vn, transaction_date, status, reseller_name
            FROM esd_licenses
            WHERE UPPER(esd_key) = ? OR UPPER(transaction_code) = ?
        """, (clean_token, clean_token))
        match = cursor.fetchone()

        if match:
            full_key = match["esd_key"]
            masked_key = full_key[:5] + "-***** -*****-" + full_key[-5:] if len(full_key) >= 20 else full_key

            rows.append({
                "no": len(rows) + 1,
                "origin_name": match["transaction_code"],
                "default_code": match["product_code"],
                "name": match["name_en"],
                "vn_name": match["name_vn"],
                "date_done": match["transaction_date"],
                "status": match["status"] or "Đã cấp hợp lệ",
                "esd_key": masked_key,
                "full_key": full_key,
                "reseller_name": match["reseller_name"],
                "is_valid": True
            })
        else:
            rows.append({
                "no": len(rows) + 1,
                "origin_name": token,
                "default_code": "—",
                "name": "Không tìm thấy trong hệ thống ESD HQN Software",
                "vn_name": "Mã ESD hoặc mã giao dịch không tồn tại trong hệ thống HQN Software",
                "date_done": "—",
                "status": "Không hợp lệ / Không tồn tại",
                "esd_key": token,
                "full_key": token,
                "reseller_name": "—",
                "is_valid": False
            })

    valid_count = sum(1 for r in rows if r["is_valid"])
    cursor.execute("""
        INSERT INTO search_logs (search_type, query_value, found_count)
        VALUES ('esd', ?, ?)
    """, (query_string, valid_count))
    conn.commit()
    conn.close()

    return rows


def search_by_contract(transaction_code: str) -> Dict[str, Any]:
    """
    Search all keys (ESD + physical) belonging to a transaction/contract code.
    Returns masked keys: first 20 chars hidden, only last 5 chars shown.
    Format: ****-****-****-****-XXXXX
    """
    if not transaction_code:
        return {"found": False, "transaction_code": transaction_code, "esd_keys": [], "physical_keys": [], "product_info": None}

    tc = transaction_code.strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()

    def mask_key(key: str) -> str:
        """Hide first 20 chars, show only last 5."""
        key = key.strip()
        if len(key) >= 25 and key[5] == '-':
            # Standard Microsoft 25-char format: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
            last_segment = key.split('-')[-1]
            return f"****-****-****-****-{last_segment}"
        elif len(key) > 5:
            return f"{'*' * (len(key) - 5)}{key[-5:]}"
        return key

    # Search ESD licenses by transaction_code
    cursor.execute("""
        SELECT esd_key, transaction_code, product_code, name_vn, name_en,
               transaction_date, status, reseller_name, customer_email, notes
        FROM esd_licenses
        WHERE UPPER(transaction_code) = ?
        ORDER BY id
    """, (tc,))
    esd_rows = cursor.fetchall()

    # Search physical licenses by transaction_code stored in customer_or_reseller or notes
    # Also check if serial belongs to a batch with this transaction code via notes field
    cursor.execute("""
        SELECT serial_number, product_code, name_vn, name_en,
               country_name, status, distributor, distribute_date, customer_or_reseller, notes
        FROM physical_licenses
        WHERE UPPER(notes) LIKE ? OR UPPER(customer_or_reseller) LIKE ?
        ORDER BY id
    """, (f'%{tc}%', f'%{tc}%'))
    physical_rows = cursor.fetchall()

    esd_keys = []
    physical_keys = []
    product_info = None

    for row in esd_rows:
        full_key = row["esd_key"]
        if product_info is None:
            product_info = {
                "product_code": row["product_code"],
                "name_vn": row["name_vn"],
                "name_en": row["name_en"],
                "transaction_date": row["transaction_date"],
                "reseller_name": row["reseller_name"],
                "status": row["status"],
            }
        esd_keys.append({
            "masked_key": mask_key(full_key),
            "last5": full_key[-5:] if len(full_key) >= 5 else full_key,
            "status": row["status"] or "Đã cấp hợp lệ",
        })

    for row in physical_rows:
        serial = row["serial_number"]
        if product_info is None:
            product_info = {
                "product_code": row["product_code"],
                "name_vn": row["name_vn"],
                "name_en": row["name_en"],
                "transaction_date": row["distribute_date"],
                "reseller_name": row["distributor"],
                "status": row["status"],
            }
        physical_keys.append({
            "masked_key": mask_key(serial),
            "last5": serial[-5:] if len(serial) >= 5 else serial,
            "status": row["status"] or "Chính hãng HQN Software",
        })

    total_keys = len(esd_keys) + len(physical_keys)

    # Log the search
    cursor.execute("""
        INSERT INTO search_logs (search_type, query_value, found_count)
        VALUES ('contract', ?, ?)
    """, (transaction_code, total_keys))
    conn.commit()
    conn.close()

    return {
        "found": total_keys > 0,
        "transaction_code": tc,
        "esd_keys": esd_keys,
        "physical_keys": physical_keys,
        "total_keys": total_keys,
        "product_info": product_info,
    }


def get_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM physical_licenses")
    total_physical = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM esd_licenses")
    total_esd = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM search_logs")
    total_searches = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM search_logs WHERE found_count > 0")
    successful_searches = cursor.fetchone()[0]

    conn.close()
    return {
        "total_physical": total_physical,
        "total_esd": total_esd,
        "total_keys": total_physical + total_esd,
        "total_searches": total_searches,
        "successful_searches": successful_searches
    }


def import_bulk_licenses(
    license_type: str,
    keys: List[str],
    product_code: str,
    name_vn: str,
    name_en: str,
    transaction_code: str = '',
    end_user: str = '',
    customer_email: str = '',
    transaction_date: str = '',
    country_name: str = 'Singapore',
    distributor: str = 'HQN Software',
    reseller_name: str = 'HQN Software',
    notes: str = ''
) -> Dict[str, Any]:
    if not keys:
        return {"success": False, "imported_count": 0, "skipped_count": 0, "total": 0, "message": "Danh sách key trống."}

    conn = get_db_connection()
    cursor = conn.cursor()

    imported_count = 0
    skipped_count = 0
    seen_in_batch = set()

    for raw_k in keys:
        k = raw_k.strip().upper()
        if not k or k in seen_in_batch:
            continue
        seen_in_batch.add(k)

        if license_type == 'physical':
            # Check existing serial
            cursor.execute("SELECT id FROM physical_licenses WHERE UPPER(serial_number) = ?", (k,))
            if cursor.fetchone():
                skipped_count += 1
                continue
            cursor.execute("""
                INSERT INTO physical_licenses
                (serial_number, product_code, name_en, name_vn, country_name, status, distributor, distribute_date, customer_or_reseller, notes)
                VALUES (?, ?, ?, ?, ?, 'Chính hãng HQN Software', ?, ?, ?, ?)
            """, (k, product_code, name_en, name_vn, country_name, distributor or 'HQN Software', transaction_date, end_user, notes))
            imported_count += 1

        else:  # esd
            # Check existing esd_key
            cursor.execute("SELECT id FROM esd_licenses WHERE UPPER(esd_key) = ?", (k,))
            if cursor.fetchone():
                skipped_count += 1
                continue
            cursor.execute("""
                INSERT INTO esd_licenses
                (esd_key, transaction_code, product_code, name_en, name_vn, transaction_date, status, reseller_name, customer_email, notes)
                VALUES (?, ?, ?, ?, ?, ?, 'Đã cấp hợp lệ', ?, ?, ?)
            """, (k, transaction_code, product_code, name_en, name_vn, transaction_date, reseller_name or 'HQN Software', customer_email, notes))
            imported_count += 1

    conn.commit()
    conn.close()

    return {
        "success": True,
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "total": len(seen_in_batch)
    }


def get_contracts_summary() -> List[Dict[str, Any]]:
    """
    Get a list of distinct transaction/contract codes and their key count.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT transaction_code, product_code, name_vn, COUNT(*) as key_count, MAX(transaction_date) as latest_date
        FROM esd_licenses
        GROUP BY transaction_code
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    contracts = [dict(r) for r in rows]
    conn.close()
    return contracts


def delete_licenses_by_contract(transaction_code: str) -> Dict[str, Any]:
    """
    Delete all keys (ESD and physical) belonging to a specific transaction/contract code.
    """
    if not transaction_code:
        return {"success": False, "total_deleted": 0, "message": "Mã hợp đồng không hợp lệ."}

    tc = transaction_code.strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Count ESD licenses before deleting
    cursor.execute("SELECT COUNT(*) FROM esd_licenses WHERE UPPER(transaction_code) = ?", (tc.upper(),))
    esd_count = cursor.fetchone()[0]

    # Delete from esd_licenses
    cursor.execute("DELETE FROM esd_licenses WHERE UPPER(transaction_code) = ?", (tc.upper(),))

    # Also check if any physical_licenses have notes or customer_or_reseller matching tc
    cursor.execute("""
        SELECT COUNT(*) FROM physical_licenses 
        WHERE UPPER(notes) = ? OR UPPER(customer_or_reseller) = ?
    """, (tc.upper(), tc.upper()))
    physical_count = cursor.fetchone()[0]

    if physical_count > 0:
        cursor.execute("""
            DELETE FROM physical_licenses 
            WHERE UPPER(notes) = ? OR UPPER(customer_or_reseller) = ?
        """, (tc.upper(), tc.upper()))

    conn.commit()
    conn.close()

    total_deleted = esd_count + physical_count
    return {
        "success": total_deleted > 0,
        "transaction_code": tc,
        "esd_deleted": esd_count,
        "physical_deleted": physical_count,
        "total_deleted": total_deleted
    }

