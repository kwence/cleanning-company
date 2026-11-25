from django.core.management.base import BaseCommand

from payroll.services import generate_payroll


class Command(BaseCommand):
    help = "Generate the monthly payroll run from approved time entries (with UK tax & NI)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--period",
            default=None,
            help="Pay period in YYYY-MM format (defaults to the current month).",
        )

    def handle(self, *args, **options):
        from django.utils import timezone

        period = options.get("period") or f"{timezone.now().year:04d}-{timezone.now().month:02d}"
        run, created = generate_payroll(period)
        action = "Created" if created else "Refreshed"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} payroll run for {period}: {run.payslip_count} payslip(s), "
                f"net {run.net_total} for gross {run.gross_total}."
            )
        )
        return 0
