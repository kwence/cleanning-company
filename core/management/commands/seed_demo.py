"""Create a ready-to-explore demo dataset for the cleaning company."""

from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounting.models import Payment
from badges.models import CleaningBadge
from banking.models import BankTransfer, EmployeeBankAccount
from banking.services import ensure_demo_company_account, ensure_employee_bank_accounts
from clients.models import Client
from employees.models import Certification, Employee
from inventory.models import Equipment, StockItem, StockMovement, StockOrder
from payroll.models import PayrollConfig, PayrollRun, Payslip
from shifts.models import Shift
from tasks.models import Task
from timeclock.models import TimeEntry

User = get_user_model()

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "DemoPass123!"


class Command(BaseCommand):
    help = "Seed demo data: staff, clients, shifts, tasks, badges, time entries, payroll and bank accounts."

    def handle(self, *args, **options):
        verbose = options.get("verbosity", 1) > 0

        # Clean slate for the demo dataset (children before parents).
        StockMovement.objects.all().delete()
        StockOrder.objects.all().delete()
        StockItem.objects.all().delete()
        Equipment.objects.all().delete()
        TimeEntry.objects.all().delete()
        Task.objects.all().delete()
        CleaningBadge.objects.all().delete()
        Certification.objects.all().delete()
        Shift.objects.all().delete()
        BankTransfer.objects.all().delete()
        Payslip.objects.all().delete()
        Payment.objects.all().delete()
        PayrollRun.objects.all().delete()
        EmployeeBankAccount.objects.all().delete()
        Employee.objects.all().delete()
        Client.objects.all().delete()
        User.objects.filter(username=DEMO_USERNAME).delete()

        # --- Staff -------------------------------------------------------------
        today = date.today()
        demo_user = User.objects.create_user(
            username=DEMO_USERNAME, email="demo@cleansweep.co.uk", first_name="Alex", password=DEMO_PASSWORD
        )
        alex = Employee.objects.create(
            user=demo_user,
            full_name="Alex Morgan",
            email="alex.morgan@cleansweep.co.uk",
            phone="07700 900100",
            job_role="manager",
            hourly_rate=18,
            employment_status="active",
            ni_number="CM123456A",
            tax_code="1257L",
            bank_sort_code="04-00-04",
            bank_account_number="12345678",
        )
        maria = Employee.objects.create(
            full_name="Maria Gonzalez",
            email="maria.gonzalez@cleansweep.co.uk",
            phone="07700 900101",
            job_role="cleaner",
            hourly_rate=12.5,
            ni_number="AB123456C",
            tax_code="1257L",
            bank_sort_code="04-00-04",
            bank_account_number="12345678",
            right_to_work_status="checked", right_to_work_check_date=today - timedelta(days=30),
            dbs_status="clear", dbs_issue_date=today - timedelta(days=120), dbs_expiry_date=today + timedelta(days=245),
            induction_completed_date=today - timedelta(days=60), health_safety_training_date=today - timedelta(days=60),
            coshh_training_date=today - timedelta(days=45), risk_assessment_ack_date=today - timedelta(days=60), ppe_provided_date=today - timedelta(days=60),
        )
        james = Employee.objects.create(
            full_name="James Okafor",
            email="james.okafor@cleansweep.co.uk",
            phone="07700 900102",
            job_role="senior_cleaner",
            hourly_rate=14,
            ni_number="CD234567D",
            tax_code="1257L",
            bank_sort_code="20-21-21",
            bank_account_number="87654321",
            right_to_work_status="checked", right_to_work_check_date=today - timedelta(days=90),
            dbs_status="not_required",
            induction_completed_date=today - timedelta(days=90), health_safety_training_date=today - timedelta(days=90),
            coshh_training_date=today - timedelta(days=90), risk_assessment_ack_date=today - timedelta(days=90), ppe_provided_date=today - timedelta(days=90),
        )
        priya = Employee.objects.create(
            full_name="Priya Sharma",
            email="priya.sharma@cleansweep.co.uk",
            phone="07700 900103",
            job_role="cleaner",
            hourly_rate=12.5,
            ni_number="EF345678E",
            tax_code="1257L",
            bank_sort_code="20-21-21",
            bank_account_number="87654321",
            right_to_work_status="follow_up", right_to_work_check_date=today - timedelta(days=10),
            dbs_status="required",
            induction_completed_date=today - timedelta(days=15),
        )

        # --- Fake bank accounts ------------------------------------------------
        ensure_demo_company_account()
        ensure_employee_bank_accounts()

        Certification.objects.create(
            employee=maria, name="COSHH Awareness", certification_type="cossh",
            issuing_body="Cleared Training", credential_id="COSHH-8842", issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
        )
        Certification.objects.create(
            employee=maria, name="DBS Check", certification_type="dbs",
            issuing_body="Disclosure & Barring Service", credential_id="DBS-5521", issue_date=date.today() - timedelta(days=200),
            expiry_date=date.today() + timedelta(days=165),
        )
        Certification.objects.create(
            employee=james, name="Manual Handling", certification_type="manual_handling",
            issuing_body="Cleared Training", credential_id="MH-3310", issue_date=date.today() - timedelta(days=90),
            expiry_date=date.today() + timedelta(days=275),
        )
        Certification.objects.create(
            employee=priya, name="COSHH Awareness", certification_type="cossh",
            issuing_body="Cleared Training", credential_id="COSHH-8843", issue_date=date.today() - timedelta(days=60),
            expiry_date=date.today() + timedelta(days=305),
        )

        # --- Clients -----------------------------------------------------------
        riverside = Client.objects.create(
            name="Riverside Care Home", contact_name="Jane Smith", email="jane@riversidecare.org",
            phone="01234 567890", address="12 Riverside Walk, London", status="active",
            notes="Two wings, hoist access, chemical storage room locked.",
        )
        maple = Client.objects.create(
            name="Maple Dental Clinic", contact_name="Dr. Lee", email="admin@mapledental.co.uk",
            phone="02034 567890", address="88 High Street, Croydon", status="active",
            notes="Ground floor only, daily disinfection of treatment rooms.",
        )

        # --- Shifts ------------------------------------------------------------
        today = date.today()
        shift_specs = [
            (maria, riverside, today - timedelta(days=1), time(9, 0), time(13, 0), "completed"),
            (maria, riverside, today, time(9, 0), time(13, 0), "completed"),
            (james, maple, today - timedelta(days=2), time(10, 0), time(14, 0), "completed"),
            (priya, riverside, today, time(14, 0), time(18, 0), "completed"),
            (james, maple, today + timedelta(days=1), time(9, 0), time(13, 0), "scheduled"),
        ]
        for employee, client, day, start, end, status in shift_specs:
            Shift.objects.create(
                employee=employee, client=client, date=day, start_time=start, end_time=end,
                status=status, notes="Deep clean" if status == "completed" else "Routine turnover",
            )

        # --- Tasks -------------------------------------------------------------
        Task.objects.create(
            client=riverside, employee=maria, title="Deep clean of lounge and bathroom",
            description="Two bathrooms, hoovering and disinfecting all surfaces.", status="in_progress",
            priority="high", due_date=today + timedelta(days=1),
        )
        Task.objects.create(
            client=maple, employee=james, title="Disinfect treatment rooms",
            description="EPA-approved disinfectant, 30 min contact time respected.", status="open",
            priority="medium", due_date=today + timedelta(days=2),
        )

        # --- Badges ------------------------------------------------------------
        CleaningBadge.objects.create(
            employee=maria, card_number="CS-000001", holder_name="Maria Gonzalez",
            issue_date=today - timedelta(days=30), expiry_date=today + timedelta(days=335), status="active",
        )
        CleaningBadge.objects.create(
            employee=james, card_number="CS-000002", holder_name="James Okafor",
            issue_date=today - timedelta(days=90), expiry_date=today + timedelta(days=275), status="active",
        )

        # --- Time entries -------------------------------------------------------
        TimeEntry.objects.create(
            employee=maria, shift=None, date=today - timedelta(days=1), clock_in=time(9, 0), clock_out=time(13, 0),
            approved=True, approved_by=demo_user,
        )
        TimeEntry.objects.create(
            employee=maria, shift=None, date=today, clock_in=time(9, 0), clock_out=time(13, 0),
            approved=True, approved_by=demo_user,
        )
        TimeEntry.objects.create(
            employee=james, shift=None, date=today - timedelta(days=2), clock_in=time(10, 0), clock_out=time(14, 0),
            approved=True, approved_by=demo_user,
        )
        TimeEntry.objects.create(
            employee=priya, shift=None, date=today, clock_in=time(14, 0), clock_out=time(18, 0),
            approved=True, approved_by=demo_user,
        )
        TimeEntry.objects.create(
            employee=james, shift=None, date=today, clock_in=time(8, 0), clock_out=time(12, 0),
            approved=False, approved_by=None,
        )

        # --- Stock -------------------------------------------------------------
        bleach = StockItem.objects.create(
            name="Thick Bleach 5L", category="detergent", sku="DET-BLEACH-5L", unit="bottle",
            supplier="CleanPro Supplies", location="Chemical store", minimum_stock=2, reorder_quantity=6,
            coshh_required=True, sds_url="https://example.com/sds/bleach.pdf",
            hazard_notes="Irritant/corrosive depending on concentration. Avoid mixing with acids.",
            ppe_notes="Gloves, eye protection, apron as per SDS.", storage_notes="Locked chemical cupboard, upright, ventilated.",
        )
        disinfectant = StockItem.objects.create(
            name="Multi-Surface Disinfectant", category="disinfectant", sku="DIS-MULTI-1L", unit="bottle",
            supplier="CleanPro Supplies", location="Chemical store", minimum_stock=4, reorder_quantity=10,
            coshh_required=True, sds_url="https://example.com/sds/disinfectant.pdf",
            hazard_notes="Follow dilution instructions. Keep away from food prep surfaces unless food-safe.",
            ppe_notes="Gloves; eye protection for decanting.", storage_notes="Original labelled container.",
        )
        mop = StockItem.objects.create(
            name="Kentucky Mop Head", category="mop", sku="MOP-KENT-001", unit="unit",
            supplier="Janitorial Direct", location="Store room A", minimum_stock=3, reorder_quantity=5,
        )
        brush = StockItem.objects.create(
            name="Scrubbing Brush", category="brush", sku="BRU-SCRUB-001", unit="unit",
            supplier="Janitorial Direct", location="Store room A", minimum_stock=2, reorder_quantity=4,
        )
        cloths = StockItem.objects.create(
            name="Microfibre Cloths (Pack of 10)", category="cloth", sku="CLO-MICRO-10", unit="pack",
            supplier="Janitorial Direct", location="Store room B", minimum_stock=2, reorder_quantity=6,
        )
        cream = StockItem.objects.create(
            name="Stainless Steel Cream Cleaner", category="cream", sku="CRM-STEEL-500", unit="bottle",
            supplier="CleanPro Supplies", location="Chemical store", minimum_stock=1, reorder_quantity=3,
            coshh_required=True, sds_url="https://example.com/sds/steel-cream.pdf",
            hazard_notes="May cause irritation. Use as directed.", ppe_notes="Gloves recommended.",
        )

        StockMovement.objects.create(item=bleach, movement_type="in", quantity=8, movement_date=today - timedelta(days=10), reference="SEED-IN", recorded_by=demo_user)
        StockMovement.objects.create(item=bleach, movement_type="out", quantity=-2, movement_date=today - timedelta(days=2), reference="JOB-RIV", recorded_by=demo_user)
        StockMovement.objects.create(item=disinfectant, movement_type="in", quantity=12, movement_date=today - timedelta(days=10), reference="SEED-IN", recorded_by=demo_user)
        StockMovement.objects.create(item=mop, movement_type="in", quantity=6, movement_date=today - timedelta(days=20), reference="SEED-IN", recorded_by=demo_user)
        StockMovement.objects.create(item=cloths, movement_type="in", quantity=5, movement_date=today - timedelta(days=8), reference="SEED-IN", recorded_by=demo_user)
        StockMovement.objects.create(item=cloths, movement_type="out", quantity=-1, movement_date=today - timedelta(days=1), reference="JOB-MAP", recorded_by=demo_user)

        StockOrder.objects.create(
            item=disinfectant, supplier="CleanPro Supplies", quantity=10, unit_cost=3.40, order_date=today - timedelta(days=3),
            expected_date=today + timedelta(days=2), status="ordered", reference="PO-1001", created_by=demo_user,
        )
        StockOrder.objects.create(
            item=brush, supplier="Janitorial Direct", quantity=4, unit_cost=2.10, order_date=today - timedelta(days=7),
            received_date=today - timedelta(days=5), status="received", reference="PO-1000", created_by=demo_user,
        )

        # --- Equipment ---------------------------------------------------------
        Equipment.objects.create(
            name="Numatic Henry Vacuum", equipment_type="vacuum", asset_tag="VAC-001", serial_number="HENRY-88421",
            location="Riverside Care Home", assigned_to=maria, status="in_use", purchase_date=today - timedelta(days=400),
            last_service_date=today - timedelta(days=60), next_service_date=today + timedelta(days=120),
            pat_test_date=today - timedelta(days=30), pat_due_date=today + timedelta(days=335),
            risk_assessment_date=today - timedelta(days=90), puwer_inspection_date=today - timedelta(days=30),
            is_safe_to_use=True, notes="Cable inspected; no defects.",
        )
        Equipment.objects.create(
            name="Kärcher Floor Scrubber", equipment_type="scrubber", asset_tag="SCR-002", serial_number="KAR-55210",
            location="Maple Dental Clinic", assigned_to=james, status="available", purchase_date=today - timedelta(days=200),
            last_service_date=today - timedelta(days=20), next_service_date=today + timedelta(days=160),
            pat_test_date=today - timedelta(days=20), pat_due_date=today + timedelta(days=345),
            risk_assessment_date=today - timedelta(days=45), puwer_inspection_date=today - timedelta(days=20),
            is_safe_to_use=True, notes="Pads replaced on last service.",
        )
        Equipment.objects.create(
            name="Steam Cleaner Pro", equipment_type="steam_cleaner", asset_tag="STM-003", serial_number="STM-2291",
            location="Store room A", assigned_to=None, status="quarantine", purchase_date=today - timedelta(days=500),
            last_service_date=today - timedelta(days=200), next_service_date=today - timedelta(days=15),
            pat_test_date=today - timedelta(days=200), pat_due_date=today - timedelta(days=10),
            risk_assessment_date=today - timedelta(days=200), puwer_inspection_date=today - timedelta(days=200),
            is_safe_to_use=False, notes="Failed PAT visual check - damaged plug. Quarantined until repaired.",
        )

        # --- Payroll -----------------------------------------------------------
        PayrollConfig.objects.get_or_create(
            pk=1,
            defaults={"pay_day": 28, "overtime_threshold": 40, "overtime_multiplier": 1.5, "tax_year": 2025},
        )
        from payroll.services import generate_payroll

        run, _created = generate_payroll(f"{today.year:04d}-{today.month:02d}")

        if verbose:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Demo data ready: {Employee.objects.count()} employees, {Client.objects.count()} clients, "
                    f"{Shift.objects.count()} shifts, {Task.objects.count()} tasks, {CleaningBadge.objects.count()} badges, "
                    f"{TimeEntry.objects.count()} time entries, {StockItem.objects.count()} stock items, {Equipment.objects.count()} equipment, "
                    f"payroll run {run.period} with {run.payslip_count} payslip(s)."
                )
            )
            self.stdout.write(f"Sign in with: {DEMO_USERNAME} / {DEMO_PASSWORD}")

        return 0
