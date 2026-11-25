# CleanSweep — Cleaning Company Management

A Django 5 + **Bootstrap 5** web app to run a cleaning company under **UK rules**:
labour management, clients, shifts, time tracking, certifications, staff badges,
tasks and automated UK payroll with emailed payslips and accounting records.

Theme: **light purple** (`core/static/cleaning/css/theme.css`).

## Features

- **Auth**: register / login / logout (staff accounts, linked to an `Employee` profile).
- **Dashboard**: today's shifts, in-progress shifts, pending time approvals, open tasks,
  upcoming shifts, active badges and the current payroll status.
- **Clients**: jobsites and commercial accounts (status, contact, notes).
- **Employees**: staff records with job roles (Cleaner, Senior Cleaner, Team Leader,
  Supervisor, Manager), hourly rate, employment status, NI number, HMRC tax code, bank
  details (sort code + account number for PAYE payments).
- **Shifts**: scheduling per employee + client, status workflow (scheduled → in progress →
  completed / cancelled).
- **Timeclock**: clock in / clock out, open-shift tracking, manager approvals. Approved
  entries feed payroll.
- **Badges**: cleaning staff ID badge issuing with card number, holder, issue/expiry dates
  and status (active / suspended / expired / lost).
- **Tasks**: cleaning checklists linked to client, employee and shift, with priority and due date.
- **Payroll**: monthly automated run from approved time entries (or fixed **salary**) with UK tax & National Insurance
  rules (2025/26), weekly overtime (after 40h at 1.5×), gross/tax/NI/net totals, employer NIC.
  - Subcontractors flagged as **CIS** have the 20% CIS deduction applied before net pay.
  - `python manage.py run_payroll --period 2026-11`
  - Issue & email payslips (SMTP, see below) and mark them as paid (accounting payments).
- **Accounting**: wage payment records per payslip (bank transfer / BACS / cash / cheque).
- **Bank payments**: pay selected payslips from a fake company bank account into each employee's
  fake personal account. Processing debits the company balance, credits the employee balance,
  marks the payslip paid and updates the accounting record. No real money moves.

## UK payroll rules (2025/26)

- Personal allowance: £12,570. Basic rate 20% up to £50,270. Higher rate 40% up to
  £125,140. Additional rate 45% above.
- Employee National Insurance: 8% over £12,570, 2% above £50,270. Employer NIC: 13.8%.
- Gross pay = approved hours × hourly rate, or fixed monthly **salary**; overtime (default after 40h/week) at 1.5×.
- CIS subcontractors: 20% CIS deduction applied to gross before net pay.

These constants live in `payroll/services.py` and can be changed via the Payroll config page.

## Email / payslip delivery

Settings in `config/settings.py` (or environment):

- `DJANGO_EMAIL_BACKEND` (default SMTP), `EMAIL_HOST` (smtp.gmail.com), `EMAIL_PORT` (587),
  `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`.

For Gmail you need an [App Password](https://support.google.com/accounts/answer/185833).

## Quick start

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py seed_demo          # demo staff, clients, shifts, tasks, badges, time entries, payroll
python3 manage.py run_payroll         # generate current month payroll run
python3 manage.py runserver 8001
```

Open <http://127.0.0.1:8001/>. Payroll payments are processed at
<http://127.0.0.1:8001/banking/> after payroll has been generated.

## Desktop app (Linux)

Build and install a self-contained executable for the current user:

```bash
packaging/build.sh
packaging/install.sh
```

This installs `~/.local/bin/cleansweep`, an application-menu entry and icon.
Data, the SQLite database and the runtime log live in
`~/.local/share/cleansweep/`. See [packaging/README.md](packaging/README.md) for
build requirements, options and uninstall instructions.

### Demo account

| Field | Value |
| --- | --- |
| Username | `demo` |
| Password | `DemoPass123!` |

The seed creates 4 employees, 2 clients, shifts, tasks, badges, approved + pending time
entries and a payroll run for the current period.

## Project layout

```
config/                 # Django settings, root urls
core/                   # dashboard, auth, base template, purple theme, money/form template tags
clients/                # Client jobsites
employees/              # Employee + Certification (COSHH, DBS, ...)
shifts/                 # Shift schedule
timeclock/              # TimeEntry clock in/out + approvals
badges/                 # CleaningBadge issuing
tasks/                  # Task checklist
payroll/                # PayrollConfig, PayrollRun, Payslip, UK rules, run_payroll command, email
accounting/             # Wage Payment records
banking/                # Fake company/employee accounts and payslip payment processing
inventory/              # Cleaning stock, orders, movements and equipment safety register
```

## Tests

```bash
python3 manage.py test
```
