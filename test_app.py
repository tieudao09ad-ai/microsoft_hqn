import sys
import json
from app import app

client = app.test_client()

print("Testing 1: Public Homepage...")
res = client.get('/')
assert res.status_code == 200
html = res.data.decode('utf-8')
assert "HQN SOFTWARE" in html
assert "Nhà phân phối chính thức của Microsoft tại Việt Nam" not in html
assert "Quản lý Database" not in html
assert "Quản lý dữ liệu Key" not in html
assert "Seri Vật Lý Trong DB" not in html
assert "Key ESD Điện Tử Trong DB" not in html
print("PASSED: Homepage contains HQN Software, no PSD/official distributor, and no admin/stats bar.")

print("Testing 2: Public Serial Search...")
res = client.get('/portal/search/serial')
assert res.status_code == 200
html = res.data.decode('utf-8')
assert "HQN Software" in html
assert "Petrosetco" not in html
print("PASSED: Serial page contains HQN Software, no Petrosetco.")

print("Testing 3: Public ESD Search...")
res = client.get('/portal/search/esd')
assert res.status_code == 200
html = res.data.decode('utf-8')
assert "HQN Software" in html
assert "Petrosetco" not in html
print("PASSED: ESD page contains HQN Software, no Petrosetco.")

print("Testing 4: Unauthenticated access to /admin...")
res = client.get('/admin')
assert res.status_code == 302, f"Expected 302 redirect, got {res.status_code}"
assert "/admin/login" in res.headers["Location"]
print("PASSED: /admin redirects unauthenticated user to /admin/login.")

print("Testing 5: Admin Login with invalid credentials...")
res = client.post('/admin/login', data={"username": "admin", "password": "wrongpassword"})
assert res.status_code == 200
assert "không chính xác" in res.data.decode('utf-8')
print("PASSED: Wrong credentials rejected.")

print("Testing 6: Admin Login with valid credentials...")
with client:
    res = client.post('/admin/login', data={"username": "admin", "password": "admin123"}, follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "Quản trị cơ sở dữ liệu bản quyền - HQN Software" in html
    assert "Seri Vật Lý Trong DB" in html
    assert "Key ESD Điện Tử Trong DB" in html
    assert "Đăng xuất" in html
    print("PASSED: Admin successfully logged in and accessed /admin with stats bar.")

    # Test Logout
    res_logout = client.get('/admin/logout', follow_redirects=True)
    assert "Cổng Đăng Nhập Quản Trị Hệ Thống" in res_logout.data.decode('utf-8')
    print("PASSED: Logout successful.")

print("\nALL ADMIN AUTH & BRANDING TESTS PASSED PERFECTLY!")
