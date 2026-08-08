from __future__ import annotations

from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from Applet.access import module_permission_required

from .forms import ChartAccountForm, CostCenterForm, GeneratePayrollJournalForm, PayrollItemAccountMappingForm
from .models import ChartAccount, CostCenter, JournalEntry, PayrollItemAccountMapping
from .services import account_balances, accounting_report_summary, generate_payroll_journal_entry, payroll_mapping_gaps


@module_permission_required("Accounting.access_accounting_module")
def dashboard(request):
    summary = accounting_report_summary()
    recent_entries = JournalEntry.objects.select_related("period").order_by("-created_at")[:8]
    return render(
        request,
        "Accounting/dashboard.html",
        {
            "summary": summary,
            "recent_entries": recent_entries,
        },
    )


@module_permission_required("Accounting.access_accounting_module")
def chart_accounts(request):
    query = request.GET.get("q", "").strip()
    accounts = ChartAccount.objects.select_related("parent").all()
    if query:
        accounts = accounts.filter(Q(code__icontains=query) | Q(name__icontains=query))
    accounts = accounts.annotate(line_count=Count("journal_lines"))
    return render(request, "Accounting/chart_accounts.html", {"accounts": accounts, "query": query})


@module_permission_required("Accounting.manage_accounting_config")
def chart_account_create(request):
    return accounting_form_view(
        request,
        ChartAccountForm,
        "Nueva cuenta contable",
        "accounting:chart_accounts",
    )


@module_permission_required("Accounting.manage_accounting_config")
def chart_account_update(request, account_id: int):
    account = get_object_or_404(ChartAccount, pk=account_id)
    return accounting_form_view(
        request,
        ChartAccountForm,
        "Editar cuenta contable",
        "accounting:chart_accounts",
        instance=account,
    )


@module_permission_required("Accounting.access_accounting_module")
def cost_centers(request):
    query = request.GET.get("q", "").strip()
    centers = CostCenter.objects.all()
    if query:
        centers = centers.filter(Q(code__icontains=query) | Q(name__icontains=query))
    centers = centers.annotate(line_count=Count("journal_lines"))
    return render(request, "Accounting/cost_centers.html", {"centers": centers, "query": query})


@module_permission_required("Accounting.manage_accounting_config")
def cost_center_create(request):
    return accounting_form_view(
        request,
        CostCenterForm,
        "Nuevo centro de costo",
        "accounting:cost_centers",
    )


@module_permission_required("Accounting.manage_accounting_config")
def cost_center_update(request, center_id: int):
    center = get_object_or_404(CostCenter, pk=center_id)
    return accounting_form_view(
        request,
        CostCenterForm,
        "Editar centro de costo",
        "accounting:cost_centers",
        instance=center,
    )


@module_permission_required("Accounting.access_accounting_module")
def mappings(request):
    query = request.GET.get("q", "").strip()
    mappings_qs = PayrollItemAccountMapping.objects.select_related("payroll_item", "account", "cost_center")
    if query:
        mappings_qs = mappings_qs.filter(
            Q(payroll_item__codigo__icontains=query)
            | Q(payroll_item__descripcion__icontains=query)
            | Q(account__code__icontains=query)
            | Q(account__name__icontains=query)
        )
    gaps = payroll_mapping_gaps()
    return render(
        request,
        "Accounting/mappings.html",
        {
            "mappings": mappings_qs,
            "query": query,
            "gaps": gaps[:20],
            "gap_count": len(gaps),
        },
    )


@module_permission_required("Accounting.manage_accounting_config")
def mapping_create(request):
    return accounting_form_view(
        request,
        PayrollItemAccountMappingForm,
        "Nuevo mapeo item-cuenta",
        "accounting:mappings",
    )


@module_permission_required("Accounting.manage_accounting_config")
def mapping_update(request, mapping_id: int):
    mapping = get_object_or_404(PayrollItemAccountMapping, pk=mapping_id)
    return accounting_form_view(
        request,
        PayrollItemAccountMappingForm,
        "Editar mapeo item-cuenta",
        "accounting:mappings",
        instance=mapping,
    )


@module_permission_required("Accounting.access_accounting_module")
def journal_entries(request):
    entries = JournalEntry.objects.select_related("period").annotate(
        line_count=Count("lines"),
        debit_sum=Sum("lines__debit"),
        credit_sum=Sum("lines__credit"),
    )
    return render(request, "Accounting/journal_entries.html", {"entries": entries})


@module_permission_required("Accounting.generate_journal_entries")
def generate_payroll_journal(request):
    form = GeneratePayrollJournalForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        journal = generate_payroll_journal_entry(
            form.cleaned_data["period"],
            replace_existing=form.cleaned_data["replace_existing"],
        )
        messages.success(request, f"Asiento generado: {journal.number}")
        return redirect("accounting:journal_detail", journal_id=journal.id)
    return render(
        request,
        "Accounting/generate_payroll_journal.html",
        {
            "form": form,
        },
    )


@module_permission_required("Accounting.access_accounting_module")
def journal_detail(request, journal_id: int):
    journal = get_object_or_404(JournalEntry.objects.select_related("period"), pk=journal_id)
    lines = journal.lines.select_related("account", "cost_center")
    return render(request, "Accounting/journal_detail.html", {"journal": journal, "lines": lines})


@module_permission_required("Accounting.view_accounting_reports")
def reports(request):
    return render(
        request,
        "Accounting/reports.html",
        {
            "summary": accounting_report_summary(),
            "balances": account_balances(),
        },
    )


def accounting_form_view(request, form_class, title: str, back_url: str, instance=None):
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Registro guardado.")
        return redirect(back_url)
    return render(
        request,
        "Accounting/model_form.html",
        {
            "form": form,
            "title": title,
            "back_url": back_url,
        },
    )
