# Helix HR QA Report

Date: 2026-09-17
Scope: Local Django HR Portal, Django tests, PyTest/Selenium configuration, source review, security smoke tests
Environment: Windows 11, Python 3.12.3, Django 4.2.30, pytest 7.4.4, Selenium 4.49.0, SQLite

## A. Executive Summary

The application starts and Django system checks pass. Database migration drift was not detected. The primary authentication and dashboard path can pass in isolation, and the live browser confirmed the main pages render.

The project is not ready for a clean QA sign-off. The Django suite produced 58 passing tests, 1 failure, and 1 error. The Selenium suite is not reliable as currently designed: fixtures depend on rows and users already present in the developer database, Firefox and Edge fixtures reference missing imports, and dashboard tests use selectors that no longer match the templates. Production security configuration also defaults to DEBUG mode and a predictable fallback SECRET_KEY.

Release recommendation: NO-GO until the high-priority configuration and test-isolation defects are fixed and the full suite passes from a clean database.

## B. Test Plan and Coverage

| Area | Planned coverage | Result |
|---|---|---|
| Setup and configuration | check, migration drift, imports, templates | PASS for check and migration drift; source risks found |
| Authentication | valid/invalid login, empty fields, redirects, logout | Django coverage mostly PASS; Selenium is unstable |
| Authorization | anonymous access to protected routes | PASS: redirects observed for dashboard; other routes should be added to regression tests |
| Employee creation | valid, required, duplicate, format, boundary | Mostly covered; one invalid-ID test is broken by test API usage |
| Search/filter | ID, name, department, no results | Django dashboard tests PASS |
| Employee profile/settings/reports | route and render smoke checks | PASS via direct authenticated requests |
| Admin | registration and configuration | Existing admin unit tests PASS; browser workflow not executed |
| Security | headers, CSRF, XSS-style inputs, settings | Partial smoke coverage; production hardening findings remain |
| Responsive/browser compatibility | Chrome, Firefox, Edge, mobile | Chrome partial; Firefox/Edge blocked by fixture defects; mobile not executed |

## C. Test Execution Matrix

| Command | Evidence | Status |
|---|---|---|
| `python manage.py check` | System check identified no issues | PASS |
| `python manage.py makemigrations --check --dry-run` | No changes detected | PASS |
| `python manage.py test portal --verbosity=2` | Ran 60; 58 passed, 1 failed, 1 error | FAIL |
| `pytest --collect-only` | 53 tests collected | PASS |
| `pytest automation` | Observed 1 pass and 5 errors in isolated run; output was affected by browser process noise | FAIL / UNSTABLE |
| Isolated Chrome dashboard test | `test_dashboard_loads_after_login` passed | PASS |
| Isolated Chrome login test | `test_successful_login` passed on rerun | PASS, flaky in prior run |
| Firefox automation | Not executed successfully | BLOCKED |
| Edge automation | Not executed successfully | BLOCKED |
| Live route smoke checks | login, settings, dashboard, employees, reports rendered | PASS |

## D. Django Functional Findings

### D-001 - Timestamp test fails because `updated_at` is not guaranteed to advance

- Severity: Medium
- Priority: P1
- Location: `portal/models.py`, `Employee.updated_at`; `portal/tests.py`, `test_updated_at_changes_on_save`
- Evidence: `AssertionError: updated_at ... not greater than ...`; both values were identical during the test.
- Impact: Consumers cannot safely rely on `updated_at` changing for rapid successive saves; the current regression test is red.
- Recommended fix: Define the required timestamp semantics explicitly. If every save must produce a strictly newer value, update the field explicitly with a monotonic timestamp or adjust the test to verify persistence and non-decrease. Prefer testing behavior required by the product rather than relying on database clock precision.
- Regression: Save an employee twice within the same clock tick and assert the selected timestamp contract.

### D-002 - Invalid employee ID test uses an incompatible Django assertion signature

- Severity: Medium
- Priority: P1
- Location: `portal/tests.py`, `EmployeeAddViewTests.test_post_invalid_employee_id`
- Evidence: Django 4.2 raises `TypeError: missing a required argument: 'errors'`, followed by `AttributeError: 'HttpResponse' object has no attribute 'is_bound'`.
- Impact: A validation test errors before asserting application behavior.
- Recommended fix: Use `self.assertFormError(response.context['form'], 'employee_id', expected_error)` for the installed Django version, or pass the required `errors` argument according to the supported API.
- Regression: Submit `emp@123`, assert HTTP 200, bound form, and the expected field error.

## E. Selenium/PyTest Findings

### D-003 - Automation fixtures depend on pre-existing database data

- Severity: High
- Priority: P1
- Location: `automation/conftest.py`, `test_user`, `admin_user`, `test_employee`, `multiple_employees`
- Evidence: Fixtures explicitly say users/employees already exist in the main database and call `.get()` for fixed IDs such as `EMP001`.
- Impact: A clean checkout, CI database, or parallel test run can fail before the test begins. Tests can mutate shared developer data and affect later tests.
- Recommended fix: Create users and employees inside isolated test fixtures. Use pytest-django database access, unique IDs per test, and cleanup/transaction isolation. Never require the developer's `db.sqlite3` contents.
- Regression: Run the suite after moving or deleting `db.sqlite3`; it should still create all required data.

### D-004 - Firefox and Edge fixtures reference undefined driver-manager classes

- Severity: High
- Priority: P1
- Location: `automation/conftest.py`
- Evidence: Firefox calls `GeckoDriverManager()` and Edge calls `EdgeChromiumDriverManager()`, but only ChromeDriverManager is imported locally.
- Impact: Firefox and Edge runs fail at driver setup with `NameError` or cannot be considered supported.
- Recommended fix: Import the corresponding classes from `webdriver_manager.firefox` and `webdriver_manager.microsoft`, or use Selenium Manager consistently and remove the custom manager dependency.
- Regression: Run one login test with `--browser=firefox` and `--browser=edge` in supported environments.

### D-005 - Dashboard action selectors in tests do not match the template

- Severity: Medium
- Priority: P1
- Location: `automation/test_dashboard.py`; `templates/dashboard.html`
- Evidence: Tests search for `data-test="action-view"`, `action-edit`, and `action-delete`; the template emits `employee-view`, `employee-edit`, and `employee-delete`.
- Impact: Action-menu coverage fails even when the UI is present.
- Recommended fix: Choose one naming contract and update either the template or tests. Add a dedicated test that opens the menu and verifies View navigation.
- Regression: Assert all three stable selectors and verify the View URL.

### D-006 - Employee Selenium tests use `By` without importing it

- Severity: Medium
- Priority: P1
- Location: `automation/test_employee.py`
- Evidence: The file calls `By.CSS_SELECTOR` but imports only pytest and page objects.
- Impact: Tests reaching those lines fail with `NameError`.
- Recommended fix: Add `from selenium.webdriver.common.by import By`.
- Regression: Run `test_form_fields_have_correct_attributes` and the success-message assertion.

### D-007 - Automation page object has a stale search submit locator

- Severity: Low
- Priority: P2
- Location: `automation/pages/login_page.py`, `DashboardPage.SEARCH_SUBMIT`; `templates/dashboard.html`
- Evidence: The page object expects `[data-test="search-submit"]`; the dashboard search form has no matching submit control and relies on form submission behavior.
- Impact: Search tests can fail or become dependent on incidental browser behavior.
- Recommended fix: Add an explicit submit button with a stable selector or submit the form through a page-object method using Enter/form submit intentionally.

## F. Security Matrix

| Check | Result | Finding |
|---|---|---|
| Authentication protection | PASS for dashboard smoke check | Add regression coverage for every new protected route |
| CSRF middleware | PASS in settings; CSRF token rendered | Logout uses POST in the current template, but view accepts GET; enforce method |
| SQL injection | No ORM injection observed in search/form paths | Add automated payload tests |
| Reflected XSS | Django autoescaping present in tested templates | Add explicit encoded-payload assertions |
| Clickjacking | `X-Frame-Options: DENY` observed | PASS |
| MIME sniffing | `X-Content-Type-Options: nosniff` observed | PASS |
| CSRF cookie | Cookie issued; Secure is false in local HTTP | Expected locally; require Secure in production |
| Debug mode | `DEBUG=True` by default | High deployment risk |
| Secret key | Fallback starts with `django-insecure-` | High deployment risk |
| Session cookies | No production Secure/HttpOnly/SameSite hardening was verified | Configure explicitly for deployment |
| Brute-force protection | Not present in code reviewed | Medium risk; add throttling/lockout at deployment boundary |
| IDOR | Employee detail uses authenticated lookup by integer PK | No role-based authorization exists; verify intended access model |
| Unsafe redirect | Login redirects to named dashboard; no user-controlled next handling found | PASS for reviewed path |

### Security defects

#### D-008 - Unsafe production defaults for DEBUG and SECRET_KEY

- Severity: High
- Priority: P0 for production deployment
- Location: `hr_portal/settings.py`
- Evidence: `DEBUG` defaults to true; `SECRET_KEY` falls back to a known `django-insecure-dev-key-change-in-production` value.
- Attack scenario: A deployment missing environment variables exposes debug tracebacks and uses a publicly guessable signing key, enabling session/token compromise risk.
- Fix: Fail fast when production settings lack a strong secret; default DEBUG to false; separate development settings; add `SECURE_SSL_REDIRECT`, secure cookies, HSTS, and deployment checks.
- Verification: Run with production environment variables absent and confirm startup fails or uses safe values; run `manage.py check --deploy`.

#### D-009 - Logout view accepts GET requests

- Severity: Medium
- Priority: P1
- Location: `portal/views.py`, `logout_view`
- Evidence: The view performs logout without checking `request.method`; the current Django test suite calls logout with GET.
- Risk: Cross-site links or crawlers can force logout. It also weakens the intended CSRF-protected POST contract.
- Fix: Require POST with `@require_POST`, keep the form POST, and update the unit test to post.
- Verification: GET returns 405; POST logs out and redirects.

## G. UI/UX and Accessibility Review

- Live smoke checks confirmed login, dashboard, employee directory, reports, settings, employee profiles, and the notification popover render.
- The bell popover was verified with `aria-expanded` and keyboard close behavior.
- Glass surfaces and responsive CSS are extensive, but mobile and cross-browser visual verification was not executed in this run.
- Notification panel content is currently static, not event-backed; this is a product limitation, not a security defect.
- The settings notification checkboxes are visual controls only; they do not persist or change server behavior.
- The Reports page performs one count query per configured department. With the current ten departments this is small, but aggregation should be considered as data grows.

## H. Boundary and Negative Test Matrix

| Field | Tested/covered | Additional required cases |
|---|---|---|
| Employee ID | required, 3-20 chars, alphanumeric, duplicate, uppercase conversion | null, 21 chars, whitespace-only, Unicode policy, SQL/XSS payloads |
| First name | required, min 2, max 50 | numbers, punctuation policy, Unicode, whitespace normalization, 51 chars |
| Last name | required, min 2, max 50 | numbers, punctuation policy, Unicode, whitespace normalization, 51 chars |
| Department | required, choices | forged choice submitted directly |
| Employment status | required, choices | forged choice submitted directly |
| Login username | empty and invalid credentials | long input, whitespace, XSS/SQL payloads, rate limiting |
| Login password | empty and invalid credentials | long input, Unicode, rate limiting, password policy |
| Search | ID/name/department/no-result | XSS/SQL payloads, whitespace-only, very long query |

## I. Recommended Fix Order

1. Replace production-unsafe DEBUG and SECRET_KEY defaults; run `manage.py check --deploy`.
2. Make Selenium fixtures self-contained and isolated from `db.sqlite3`.
3. Fix Firefox/Edge imports or standardize on Selenium Manager.
4. Align dashboard selectors and add missing `By` import.
5. Fix the Django `assertFormError` test API usage.
6. Decide and implement the `updated_at` contract.
7. Enforce POST-only logout and update its tests.
8. Add route tests for Employees, Reports, Settings, and employee detail.
9. Add responsive/browser matrix execution in CI.

## J. Regression Plan

Run from `D:\My Work\portal\hr_portal`:

```powershell
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test portal --verbosity=2
pytest -v --tb=short
pytest automation -v --browser=chrome --headless
pytest automation -v --browser=firefox --headless
pytest automation -v --browser=edge --headless
```

Before Selenium execution, the suite must create its own test user and employees. Do not rely on the existing developer database.

## K. QA Sign-off

Current sign-off: NOT APPROVED.

Minimum exit criteria:

- Django test suite: 100% pass with zero errors.
- Selenium Chrome suite: repeatable pass from a clean database.
- Firefox and Edge: either passing or explicitly removed from supported-browser claims.
- `manage.py check --deploy`: no unresolved production security warnings.
- Protected-route, CSRF, logout, IDOR, and boundary tests added and passing.
- Mobile viewport smoke checks completed.

## L. Evidence Limitations

No destructive tests, high-volume load tests, external-site tests, or production deployment tests were performed. PostgreSQL, Firefox, Edge, and real multi-user permission scenarios were not executed in this environment. Those results are NOT EXECUTED, not assumed to pass.
