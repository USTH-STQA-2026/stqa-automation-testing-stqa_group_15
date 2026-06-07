# STQA A2 Test Report

## Environment

| Item | Value |
| --- | --- |
| Application | https://stqa.rbc.vn |
| Assignment | A2 - Web UI Automation Testing |
| Framework | pytest + Playwright Python |
| Browser | Chromium |
| UI technology | Flutter Web CanvasKit with Semantics Tree |
| Main test account | `ba.nguyen@email.com` |
| Verification command | `pytest -v -s` |
| Latest result | `24 passed, 6 failed` (6 failures document real system bugs) |

## Required Test Cases

| TC | Test case | SRS | Expected result | Actual result | Status | Screenshot |
| --- | --- | --- | --- | --- | --- | --- |
| TC-01 | Login success | REQ-01 | Valid user reaches the main page and sees user information or logout control. | Main page opened and logout/user UI was visible. | PASS | `screenshots/login_success.png` |
| TC-02 | Login fails with wrong password | REQ-01 | Error `Mật khẩu không đúng`; user remains on login page. | Expected error appeared and login page stayed visible. | PASS | `screenshots/login_fail_wrong_password.png` |
| TC-03 | Login fails with empty fields | REQ-01 | Error `Vui lòng nhập email và mật khẩu`; user remains on login page. | Expected validation error appeared. | PASS | `screenshots/login_fail_empty_fields.png` |
| TC-04 | Search book by name | REQ-03 | Searching `Flutter` shows at least one Flutter book. | `Lập trình Flutter cơ bản` was found in search results. | PASS | `screenshots/search_book_by_name.png` |
| TC-05 | Search with no result | REQ-03 | Searching a non-existent keyword shows `Không tìm thấy sách` and no book card. | No-result message appeared and book list was empty. | PASS | `screenshots/search_book_no_result.png` |
| TC-06 | Filter by category | REQ-03 | Filtering `Công nghệ` shows only books in the Công nghệ category. | Every visible result belonged to `Công nghệ`. | PASS | `screenshots/filter_by_category.png` |
| TC-07 | Search book by author | REQ-03 | Searching `Nguyễn Minh Đức` shows books by that author. | All asserted results contained `Nguyễn Minh Đức`. | PASS | `screenshots/search_by_author.png` |
| TC-08 | Borrow an available book | REQ-04 | Available book can be borrowed and changes to borrowed state. | Borrow action completed and borrowed state was visible. | PASS | `screenshots/borrow_book.png` |
| TC-09 | View borrowed books | REQ-08 | Borrowed records are visible in the `Mượn / Trả` tab. | Borrowed record and return action were visible. | PASS | `screenshots/view_borrowed_books.png` |
| TC-10 | Return borrowed book | REQ-05 | Returning a borrowed book changes record/book status to returned or available. | Return action completed and returned/available state was visible. | PASS | `screenshots/return_book.png` |
| TC-11 | Logout | REQ-01 | User returns to login screen after logout. | Login UI with `Đăng nhập` and `Email` was visible. | PASS | `screenshots/logout.png` |
| TC-12 | Switch language to English | SRS 5 | UI switches from Vietnamese to English. | English UI text such as `Sign out` was visible. | PASS | `screenshots/switch_language_to_english.png` |

## Bonus Test Cases

| ID | Test case | Requirement | Expected result | Actual result | Status | Screenshot |
| --- | --- | --- | --- | --- | --- | --- |
| B-01 | Unknown email login | REQ-01 | Error `Không tìm thấy thành viên`. | Expected error appeared. | PASS | `screenshots/bonus_login_unknown_email.png` |
| B-02 | Wrong password via data-driven login | REQ-01 | Error `Mật khẩu không đúng`. | Expected error appeared. | PASS | `screenshots/bonus_login_wrong_password_param.png` |
| B-03 | Empty login via data-driven login | REQ-01 | Error `Vui lòng nhập email và mật khẩu`. | Expected error appeared. | PASS | `screenshots/bonus_login_empty_param.png` |
| B-04 | Case-insensitive search | REQ-03 | Lowercase `flutter` finds Flutter book. | Flutter book was found. | PASS | `screenshots/bonus_search_case_insensitive.png` |
| B-05 | Suspended member cannot borrow | REQ-04 | Borrow is rejected with suspended-member reason. | Rejection message for suspended member was visible. | PASS | `screenshots/bonus_suspended_member_cannot_borrow.png` |
| B-06 | Expired member cannot borrow | REQ-04 | Borrow is rejected with expired-member reason, not suspended reason. | Rejection message included `hết hạn` and not `tạm ngưng`. | PASS | `screenshots/bonus_expired_member_cannot_borrow.png` |
| B-07 | View book list after login | REQ-02 | Book list shows book code, title, author, category, and status. | Book cards contained required information. | PASS | `screenshots/bonus_view_book_list.png` |
| B-08 | Borrowed book is not treated as available | REQ-04 | Already borrowed books do not expose the same borrow availability as available books. | Borrow controls matched available book count. | PASS | `screenshots/bonus_borrow_already_borrowed.png` |

## Missing Coverage Tests

Tests covering requirements not addressed by the 12 required TCs. Failures are **intentional bug documentation** per assignment guidelines.

| ID | Test case | REQ | Expected result | Actual result | Status | Screenshot |
| --- | --- | --- | --- | --- | --- | --- |
| MC-01 | Return overdue book shows warning | REQ-05 | Warning about overdue shown when returning a late book. | App shows "Trả sách thành công" with no overdue warning. | ❌ BUG | `screenshots/return_overdue_warning.png` |
| MC-02 | Borrow limit 3 books | REQ-04 | 4th borrow attempt rejected; max 3 books allowed. | App allows 4th borrow without rejection. | ❌ BUG | `screenshots/borrow_limit_exceeded.png` |
| MC-03 | Member sees only own borrow records | REQ-08 | Member does not see other members' records in Mượn/Trả tab. | Only own records were visible. | ✅ PASS | `screenshots/member_borrow_isolation.png` |
| MC-04 | Add member with invalid email (no dot in domain) | REQ-07 | Email `testuser@invaliddomain` rejected. | App accepts invalid email and creates member. | ❌ BUG | `screenshots/add_member_invalid_email.png` |
| MC-05 | Add member with duplicate email | REQ-07 | Duplicate email rejected with error message. | Duplicate email was rejected correctly. | ✅ PASS | `screenshots/add_member_duplicate_email.png` |
| MC-06 | Add member success | REQ-07 | Valid member added successfully. | New member created successfully. | ✅ PASS | `screenshots/add_member_success.png` |
| MC-07 | Librarian detects overdue books | REQ-06 | Clicking "Kiểm tra sách quá hạn" updates BR001 to "Quá hạn". | BR001 status updated to Quá hạn as expected. | ✅ PASS | `screenshots/detect_overdue.png` |
| MC-08 | Borrow limit enforced at 3 (dialog path) | REQ-04 | 4th borrow rejected after confirmation dialog. | App completes 4th borrow; limit is effectively 4, not 3. | ❌ BUG | `screenshots/bug04_borrow_4th_attempt.png` |
| MC-09 | Member cannot lookup another member's records | REQ-08 | Search for MEM002 returns no results for non-owner. | App displays full history of MEM002 to any member. | ❌ BUG | `screenshots/bug05_lookup_mem002.png` |
| MC-10 | Member cannot return book for another member | REQ-08 | Return action on another member's record is rejected. | App allows returning another member's book without permission check. | ❌ BUG | `screenshots/bug06_return_other_member_book.png` |

## Coverage Summary

| Rubric item | Evidence |
| --- | --- |
| Complete test cases | 12/12 required tests implemented, plus 8 bonus tests, plus 10 missing coverage tests. Total: 30 automated tests. |
| Code quality | Assertions check concrete UI text, book status, validation messages, category/author constraints, and bug documentation. |
| Flutter Web handling | Tests use Semantics Tree selectors and provided helpers from `conftest.py`. |
| Screenshot and evidence | Each required, bonus, and missing coverage test saves a named screenshot in `screenshots/`. |
| Teamwork and format | README contains team information and updated test status; this report documents expected and actual results including bug findings. |

## AI Usage Disclosure

AI assistance was used to plan the test strategy, draft report content, and review coverage against the rubric. The team executed the tests, checked screenshots, and verified actual behavior against the SRS.
