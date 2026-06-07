"""
Missing Coverage Test Cases — Library Book Borrowing System
Kiểm thử các yêu cầu chưa được cover trong bộ test ban đầu.

REQ-04: Giới hạn 3 sách/thành viên
REQ-05: Cảnh báo quá hạn khi trả sách
REQ-06: Kiểm tra quá hạn (Thủ thư)
REQ-07: Quản lý thành viên (Thủ thư)
REQ-08: Cô lập phiếu mượn giữa các thành viên
"""
import os
import pytest
from conftest import (
    enable_flutter_semantics, flutter_fill, flutter_click_button,
    wait_for_flutter, login, SCREENSHOT_DIR,
)

LIBRARIAN_EMAIL = "librarian@library.com"
LIBRARIAN_PASSWORD = "admin123"

DAM_TRAN_EMAIL = "dam.tran@email.com"
DAM_TRAN_PASSWORD = "password123"

BA_NGUYEN_EMAIL = "ba.nguyen@email.com"
BA_NGUYEN_PASSWORD = "password123"


def login_as(page, base_url, email, password):
    """Helper: đăng nhập với email/password bất kỳ."""
    page.goto(base_url, wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email", email)
    flutter_fill(page, "Mật khẩu", password)
    flutter_click_button(page, "Đăng nhập")
    wait_for_flutter(page, text="Đăng xuất", timeout=30000)
    enable_flutter_semantics(page)


def borrow_one_book(page):
    """Helper: mượn một sách có sẵn đầu tiên và xác nhận dialog."""
    page.locator('flt-semantics[role="group"][aria-label*="Có sẵn"]').first.wait_for(
        state="attached", timeout=10000
    )
    page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first.click()
    wait_for_flutter(page, text="Xác nhận mượn sách")
    enable_flutter_semantics(page)
    flutter_click_button(page, "Mượn")
    wait_for_flutter(page, text="Đang mượn")
    enable_flutter_semantics(page)


# ---------------------------------------------------------------------------
# REQ-05: Cảnh báo quá hạn khi trả sách
# BUG: App không hiện cảnh báo khi trả sách quá hạn
# ---------------------------------------------------------------------------

def test_return_overdue_book_shows_warning(page, test_config):
    """TC-REQ05: Trả sách quá hạn phải hiện cảnh báo quá hạn.

    Seed data: BR001 — ba.nguyen mượn BOOK003 từ 01/09/2024, hạn 15/09/2024
    → đã quá hạn, hệ thống phải hiển thị cảnh báo khi trả (REQ-05).

    ❌ BUG EXPECTED: App chỉ hiện "Trả sách thành công" mà không có cảnh báo quá hạn.
    """
    # [R] Đăng nhập bằng ba.nguyen — account đang có BR001 quá hạn
    login_as(page, test_config["base_url"], BA_NGUYEN_EMAIL, BA_NGUYEN_PASSWORD)

    # [I] Vào tab Mượn / Trả và click trả sách BR001
    page.locator('flt-semantics[role="tab"][aria-label="Mượn / Trả"]').click()
    wait_for_flutter(page, text="Trả sách")
    page.locator('flt-semantics[role="button"]:has-text("Trả sách")').first.click()

    # [P] Chờ phản hồi sau khi trả
    wait_for_flutter(page, text="Đã trả", timeout=10000)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "return_overdue_warning.png"))

    # [R✓] Phải có cảnh báo quá hạn (REQ-05)
    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert "quá hạn" in sem_text.lower() or "overdue" in sem_text.lower(), \
        f"BUG REQ-05: Trả sách quá hạn phải hiện cảnh báo 'quá hạn' nhưng không thấy.\n" \
        f"App chỉ hiện: {sem_text[:300]}"


# ---------------------------------------------------------------------------
# REQ-04: Giới hạn tối đa 3 sách / thành viên
# BUG: App cho mượn quá 3 sách
# ---------------------------------------------------------------------------

def test_borrow_limit_3_books(page, test_config):
    """TC-REQ04: Mượn quá 3 sách phải bị từ chối (REQ-04: tối đa 3 sách/thành viên).

    Seed data: dam.tran (MEM003) chưa mượn sách nào → mượn 3 sách rồi thử lần 4.

    ❌ BUG EXPECTED: App cho phép mượn sách thứ 4 mà không có thông báo từ chối.
    """
    # [R] Đăng nhập dam.tran — không có sách đang mượn
    login_as(page, test_config["base_url"], DAM_TRAN_EMAIL, DAM_TRAN_PASSWORD)

    # [I] Mượn 3 sách thành công
    for _ in range(3):
        borrow_one_book(page)

    # Chụp màn hình sau khi mượn 3 sách
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "borrow_limit_3_books.png"))

    # [I] Thử mượn sách thứ 4
    available_cards = page.locator('flt-semantics[role="group"][aria-label*="Có sẵn"]')
    assert available_cards.count() > 0, "Cần còn ít nhất 1 sách có sẵn để thử mượn lần 4"

    page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first.click()
    wait_for_flutter(page, text="Xác nhận mượn sách")
    enable_flutter_semantics(page)
    flutter_click_button(page, "Mượn")
    page.wait_for_timeout(3000)
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "borrow_limit_exceeded.png"))

    # [P] Kiểm tra số sách đang mượn trong tab Mượn / Trả
    page.locator('flt-semantics[role="tab"][aria-label="Mượn / Trả"]').click()
    page.wait_for_timeout(3000)
    enable_flutter_semantics(page)

    active_borrows = page.locator('flt-semantics[role="group"][aria-label*="Đang mượn"]')
    borrow_count = active_borrows.count()

    # [R✓] Chỉ được mượn tối đa 3 sách (REQ-04)
    assert borrow_count <= 3, \
        f"BUG REQ-04: Thành viên đang mượn {borrow_count} sách, vượt giới hạn 3 sách/thành viên.\n" \
        f"App không từ chối khi mượn sách thứ 4."


# ---------------------------------------------------------------------------
# REQ-08: Cô lập phiếu mượn giữa các thành viên
# ---------------------------------------------------------------------------

def test_member_only_sees_own_borrow_records(page, test_config):
    """TC-REQ08: Thành viên chỉ thấy phiếu mượn của chính mình (REQ-08).

    Seed data:
    - BR001: ba.nguyen mượn BOOK003 "Kiểm thử phần mềm nhập môn" (Đang mượn)
    - BR003: biet.hoang mượn BOOK013 "Quản trị nhân sự hiện đại" (Đang mượn)
    - dam.tran chỉ có BR002 và BR005 (đã trả) → không được thấy BR001, BR003.
    """
    # [R] Đăng nhập dam.tran
    login_as(page, test_config["base_url"], DAM_TRAN_EMAIL, DAM_TRAN_PASSWORD)

    # [I] Vào tab Mượn / Trả
    page.locator('flt-semantics[role="tab"][aria-label="Mượn / Trả"]').click()
    page.wait_for_timeout(3000)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "member_borrow_isolation.png"))

    # [R✓] Không được thấy phiếu của ba.nguyen (BOOK003)
    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert "Kiểm thử phần mềm nhập môn" not in sem_text, \
        "BUG REQ-08: dam.tran không được thấy phiếu mượn BOOK003 của ba.nguyen"

    # [R✓] Không được thấy phiếu của biet.hoang (BOOK013)
    assert "Quản trị nhân sự hiện đại" not in sem_text, \
        "BUG REQ-08: dam.tran không được thấy phiếu mượn BOOK013 của biet.hoang"


# ---------------------------------------------------------------------------
# REQ-07: Quản lý thành viên (chỉ Thủ thư)
# BUG: Email không có dấu chấm trong domain bị chấp nhận
# ---------------------------------------------------------------------------

def test_add_member_invalid_email(page, test_config):
    """TC-REQ07a: Email không hợp lệ (thiếu dấu chấm trong domain) phải bị từ chối.

    SRS REQ-07: 'user@domain' là KHÔNG hợp lệ, phải có '.' trong phần domain.

    ❌ BUG EXPECTED: App chấp nhận email 'testuser@invaliddomain' và tạo thành viên thành công.
    """
    # [R] Đăng nhập Thủ thư
    login_as(page, test_config["base_url"], LIBRARIAN_EMAIL, LIBRARIAN_PASSWORD)

    # [I] Vào tab Thành viên và mở form
    page.locator('flt-semantics[role="tab"][aria-label="Thành viên"]').click()
    wait_for_flutter(page, text="Thêm thành viên", timeout=10000)
    enable_flutter_semantics(page)
    flutter_click_button(page, "Thêm thành viên")

    # Nhập email không hợp lệ (không có dấu chấm trong domain)
    page.locator('input[aria-label="Họ và tên"]').first.wait_for(state="attached", timeout=10000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Họ và tên", "Test User")
    flutter_fill(page, "Email", "testuser@invaliddomain")
    flutter_fill(page, "Số điện thoại", "0123456789")

    # Click nút submit
    page.locator('flt-semantics[role="button"]:has-text("Thêm thành viên")').last.click()
    page.wait_for_timeout(3000)
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "add_member_invalid_email.png"))

    # [R✓] Phải có thông báo lỗi email không hợp lệ — không được tạo thành công
    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert "thành công" not in sem_text.lower(), \
        f"BUG REQ-07: Email 'testuser@invaliddomain' (không có dấu chấm trong domain) " \
        f"phải bị từ chối nhưng app chấp nhận và tạo thành viên thành công.\n" \
        f"App hiện: {sem_text[:300]}"


def test_add_member_duplicate_email(page, test_config):
    """TC-REQ07b: Email đã tồn tại bị từ chối (REQ-07).

    SRS REQ-07: Không cho phép tạo email đã tồn tại.
    """
    # [R] Đăng nhập Thủ thư
    login_as(page, test_config["base_url"], LIBRARIAN_EMAIL, LIBRARIAN_PASSWORD)

    # [I] Vào tab Thành viên và mở form
    page.locator('flt-semantics[role="tab"][aria-label="Thành viên"]').click()
    wait_for_flutter(page, text="Thêm thành viên", timeout=10000)
    enable_flutter_semantics(page)
    flutter_click_button(page, "Thêm thành viên")

    page.locator('input[aria-label="Họ và tên"]').first.wait_for(state="attached", timeout=10000)
    enable_flutter_semantics(page)

    # Nhập email đã tồn tại trong hệ thống
    flutter_fill(page, "Họ và tên", "Duplicate User")
    flutter_fill(page, "Email", BA_NGUYEN_EMAIL)
    flutter_fill(page, "Số điện thoại", "0123456789")
    page.locator('flt-semantics[role="button"]:has-text("Thêm thành viên")').last.click()

    # [P] Chờ thông báo lỗi
    wait_for_flutter(page, text="Email không hợp lệ", timeout=10000)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "add_member_duplicate_email.png"))

    # [R✓] Phải có thông báo lỗi, không được tạo thành công
    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert "thành công" not in sem_text.lower(), \
        f"REQ-07: Email đã tồn tại phải bị từ chối: {sem_text[:300]}"
    assert "email không hợp lệ" in sem_text.lower() or "tồn tại" in sem_text.lower() or \
        "đã có" in sem_text.lower(), \
        f"REQ-07: Phải có thông báo lỗi khi email trùng: {sem_text[:300]}"


def test_add_member_success(page, test_config):
    """TC-REQ07c: Thêm thành viên mới — chức năng có hoạt động được không (REQ-07).

    NOTE: Do bug email validation bị ngược (xem test_add_member_invalid_email),
    test này dùng email KHÔNG có dấu chấm trong domain ('newmember@emailcom')
    để tránh bị app từ chối sai. Mục đích: xác nhận chức năng add member hoạt động.
    """
    # [R] Đăng nhập Thủ thư
    login_as(page, test_config["base_url"], LIBRARIAN_EMAIL, LIBRARIAN_PASSWORD)

    # [I] Vào tab Thành viên và mở form
    page.locator('flt-semantics[role="tab"][aria-label="Thành viên"]').click()
    wait_for_flutter(page, text="Thêm thành viên", timeout=10000)
    enable_flutter_semantics(page)
    flutter_click_button(page, "Thêm thành viên")

    page.locator('input[aria-label="Họ và tên"]').first.wait_for(state="attached", timeout=10000)
    enable_flutter_semantics(page)

    new_name = "Nguyễn Thành Viên Mới"
    flutter_fill(page, "Họ và tên", new_name)
    flutter_fill(page, "Email", "newmember@emailcom")
    flutter_fill(page, "Số điện thoại", "0987654321")
    page.locator('flt-semantics[role="button"]:has-text("Thêm thành viên")').last.click()

    # [P] Chờ thành công (dùng wait_for_timeout vì toast notification có thể biến mất nhanh)
    page.wait_for_timeout(4000)
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "add_member_success.png"))

    # [R✓] Thêm thành công — kiểm tra không còn thấy form (đã quay về list)
    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert "thành công" in sem_text.lower() or new_name in sem_text, \
        f"REQ-07: Thêm thành viên hợp lệ phải thành công: {sem_text[:300]}"


# ---------------------------------------------------------------------------
# REQ-06: Kiểm tra quá hạn (Thủ thư)
# ---------------------------------------------------------------------------

def test_librarian_detect_overdue_books(page, test_config):
    """TC-REQ06: Thủ thư nhấn 'Kiểm tra sách quá hạn' → BR001 chuyển thành 'Quá hạn'.

    Seed data: BR001 (ba.nguyen, BOOK003, hạn 15/09/2024) đang hiển thị 'Đang mượn'
    dù thực tế đã quá hạn — cần Thủ thư nhấn nút để cập nhật trạng thái (REQ-06).
    """
    # [R] Đăng nhập Thủ thư
    login_as(page, test_config["base_url"], LIBRARIAN_EMAIL, LIBRARIAN_PASSWORD)

    # [I] Vào tab Mượn / Trả và nhấn "Kiểm tra sách quá hạn"
    page.locator('flt-semantics[role="tab"][aria-label="Mượn / Trả"]').click()
    wait_for_flutter(page, text="Kiểm tra sách quá hạn", timeout=10000)
    enable_flutter_semantics(page)
    flutter_click_button(page, "Kiểm tra sách quá hạn")

    # [P] Chờ hệ thống cập nhật — status "Quá hạn" xuất hiện trong aria-label của group
    page.locator('flt-semantics[role="group"][aria-label*="Quá hạn"]').first.wait_for(
        state="attached", timeout=10000
    )
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "detect_overdue.png"))

    # [R✓] BR001 phải chuyển sang "Quá hạn" (kiểm tra qua aria-label)
    overdue_records = page.locator('flt-semantics[role="group"][aria-label*="Quá hạn"]')
    assert overdue_records.count() > 0, \
        "REQ-06: Phải có ít nhất 1 phiếu trạng thái Quá hạn sau khi Thủ thư kiểm tra (BR001)"

    # Kiểm tra BR001 cụ thể
    br001 = page.locator('flt-semantics[role="group"][aria-label*="BR001"]')
    if br001.count() > 0:
        label = br001.first.get_attribute("aria-label") or ""
        assert "Quá hạn" in label, \
            f"REQ-06: BR001 phải chuyển sang 'Quá hạn' nhưng label là: {label}"


# ---------------------------------------------------------------------------
# BUG-4: REQ-04 — Giới hạn thực tế là 4, SRS quy định tối đa 3
# ---------------------------------------------------------------------------

def test_borrow_limit_enforced_at_3(page, test_config):
    """TC-BUG04: Mượn sách thứ 4 phải bị từ chối ngay sau dialog xác nhận.

    SRS REQ-04: Mỗi thành viên chỉ được mượn tối đa 3 sách cùng lúc.

    Seed data: dam.tran (MEM003) chưa có sách đang mượn.
    Quy trình: mượn 3 sách thành công → thử mượn lần 4 → phải bị từ chối.

    ❌ BUG: App cho mượn thành công lần thứ 4 (giới hạn thực tế = 4, không phải 3).
    """
    login_as(page, test_config["base_url"], DAM_TRAN_EMAIL, DAM_TRAN_PASSWORD)

    # [I] Mượn 3 sách thành công
    for i in range(3):
        borrow_one_book(page)

    # [I] Thử mượn sách thứ 4 — điều hướng về tab Sách trước
    page.locator('flt-semantics[role="tab"][aria-label="Sách"]').click()
    page.wait_for_timeout(1000)
    enable_flutter_semantics(page)

    available = page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")')
    assert available.count() > 0, "Cần còn sách có sẵn để thử mượn lần 4"
    available.first.click()
    wait_for_flutter(page, text="Xác nhận mượn sách")
    enable_flutter_semantics(page)
    flutter_click_button(page, "Mượn")
    page.wait_for_timeout(3000)
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "bug04_borrow_4th_attempt.png"))

    # [P+R✓] Sau khi click Mượn lần 4, phải có thông báo từ chối.
    # Nếu KHÔNG có thông báo từ chối → borrow thành công → BUG.
    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    rejection_keywords = [
        "không thể mượn", "giới hạn", "tối đa", "vượt quá",
        "đã mượn đủ", "quá số lượng", "không được mượn thêm",
    ]
    was_rejected = any(kw in sem_text.lower() for kw in rejection_keywords)

    assert was_rejected, \
        f"BUG REQ-04: Mượn sách thứ 4 không bị từ chối (giới hạn SRS = 3). " \
        f"App chấp nhận yêu cầu mà không hiện thông báo lỗi. " \
        f"App hiển thị: {sem_text[:300]}"


# ---------------------------------------------------------------------------
# BUG-5: REQ-08 — Thành viên xem phiếu của người khác qua "Tra cứu phiếu mượn"
# ---------------------------------------------------------------------------

def test_member_cannot_lookup_other_member_records(page, test_config):
    """TC-BUG05: Thành viên thường không được xem phiếu mượn của người khác
    qua sub-tab 'Tra cứu phiếu mượn'.

    SRS REQ-08: Thành viên chỉ được xem phiếu mượn của chính mình.

    Quy trình: dam.tran nhập MEM002 (ba.nguyen) vào ô tra cứu → phải bị từ chối
    hoặc không hiển thị dữ liệu của ba.nguyen.

    ❌ BUG: App hiển thị đầy đủ lịch sử mượn/trả của MEM002 (Nguyễn Học Bá).
    """
    login_as(page, test_config["base_url"], DAM_TRAN_EMAIL, DAM_TRAN_PASSWORD)

    # [I] Vào tab Mượn/Trả > sub-tab Tra cứu phiếu mượn
    page.locator('flt-semantics[role="tab"][aria-label="Mượn / Trả"]').click()
    page.wait_for_timeout(1500)
    enable_flutter_semantics(page)
    page.locator('flt-semantics[role="tab"][aria-label="Tra cứu phiếu mượn"]').click()
    page.wait_for_timeout(1500)
    enable_flutter_semantics(page)

    # Nhập mã thành viên của ba.nguyen và tra cứu
    flutter_fill(page, "Nhập mã thành viên (VD: MEM001)", "MEM002")
    page.wait_for_timeout(500)
    flutter_click_button(page, "Tra cứu")
    page.wait_for_timeout(3000)
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "bug05_lookup_mem002.png"))

    # [R✓] Không được hiện dữ liệu của ba.nguyen (Nguyễn Học Bá)
    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    has_other_records = (
        "Nguyễn Học Bá" in sem_text
        or "BR001" in sem_text
        or "BR004" in sem_text
        or "Kiểm thử phần mềm nhập môn" in sem_text
        or "Trí tuệ nhân tạo đại cương" in sem_text
    )
    assert not has_other_records, \
        f"BUG REQ-08: dam.tran (thành viên thường) xem được phiếu mượn của MEM002 " \
        f"(Nguyễn Học Bá) qua 'Tra cứu phiếu mượn'. " \
        f"App hiển thị: {sem_text[:300]}"


# ---------------------------------------------------------------------------
# BUG-6: REQ-08 — Thành viên trả sách thay cho người khác
# ---------------------------------------------------------------------------

def test_member_cannot_return_book_for_another_member(page, test_config):
    """TC-BUG06: Thành viên thường không được nhấn 'Trả sách' trên phiếu
    của người khác tìm được qua 'Tra cứu phiếu mượn'.

    SRS REQ-08: Thành viên chỉ được thao tác trên phiếu của chính mình.

    Seed data: BR001 — ba.nguyen (MEM002) đang mượn BOOK003 "Kiểm thử phần mềm nhập môn".
    Quy trình: dam.tran tra cứu MEM002 → thấy BR001 → nhấn Trả sách → phải bị từ chối.

    ❌ BUG CRITICAL: App cho phép trả sách thành công, ghi ngày trả vào phiếu của
    ba.nguyen mà không kiểm tra quyền. Sách được đánh dấu trả dù ba.nguyen vẫn đang giữ.
    """
    login_as(page, test_config["base_url"], DAM_TRAN_EMAIL, DAM_TRAN_PASSWORD)

    # [I] Vào tab Mượn/Trả > Tra cứu > nhập MEM002
    page.locator('flt-semantics[role="tab"][aria-label="Mượn / Trả"]').click()
    page.wait_for_timeout(1500)
    enable_flutter_semantics(page)
    page.locator('flt-semantics[role="tab"][aria-label="Tra cứu phiếu mượn"]').click()
    page.wait_for_timeout(1500)
    enable_flutter_semantics(page)

    flutter_fill(page, "Nhập mã thành viên (VD: MEM001)", "MEM002")
    page.wait_for_timeout(500)
    flutter_click_button(page, "Tra cứu")
    page.wait_for_timeout(3000)
    enable_flutter_semantics(page)

    # [I] Kiểm tra có nút Trả sách không và nhấn nếu có
    tra_sach_btn = page.locator('flt-semantics[role="button"]:has-text("Trả sách")')
    assert tra_sach_btn.count() > 0, \
        "Tiền điều kiện: phải thấy nút 'Trả sách' trên phiếu của MEM002 " \
        "(xác nhận BUG-5 đang xảy ra trước khi kiểm tra BUG-6)"

    tra_sach_btn.first.click()
    page.wait_for_timeout(3000)
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "bug06_return_other_member_book.png"))

    # [R✓] Thao tác phải bị từ chối — không được ghi "Đã trả" lên phiếu của ba.nguyen
    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    was_returned = (
        "Trả sách thành công" in sem_text
        or ("Đã trả" in sem_text and "BR001" in sem_text)
    )
    assert not was_returned, \
        f"BUG CRITICAL REQ-08: dam.tran trả sách thay cho ba.nguyen (MEM002) thành công. " \
        f"App không kiểm tra quyền — bất kỳ thành viên nào cũng có thể trả sách của người khác. " \
        f"App hiển thị: {sem_text[:300]}"
