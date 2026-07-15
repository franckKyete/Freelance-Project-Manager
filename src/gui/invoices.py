"""Invoices screen — generate, view, and pay invoices."""

import tkinter as tk
from tkinter import messagebox

from src.services.invoice_service import InvoiceService
from src.services.client_service import ClientService
from src.services.project_service import ProjectService
from src.models.invoice import Invoice
from src.exceptions.app_exceptions import (
    InvoiceAlreadyPaidException, DuplicateInvoiceException,
)
from src.gui.theme import (
    BG_DARK, BG_CARD, ACCENT, ACCENT_2, SUCCESS, WARNING, DANGER,
    FG_PRIMARY, FG_SECONDARY, FG_MUTED, BORDER,
    FONT_H2, FONT_H3, FONT_BODY, FONT_SMALL,
    CONTENT_PAD, CARD_PAD,
)
from src.gui.widgets import (
    make_button, make_danger_button, make_scrolled_tree,
    make_combobox, field_row, section_title, confirm_dialog, status_badge,
)
from src.utils.validators import format_currency


class InvoicesFrame(tk.Frame):
    """Invoice management screen."""

    def __init__(self, parent: tk.Frame) -> None:
        super().__init__(parent, bg=BG_DARK)
        self._svc = InvoiceService()
        self._client_svc = ClientService()
        self._project_svc = ProjectService()
        self._selected: Invoice | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.pack(fill=tk.BOTH, expand=True, padx=CONTENT_PAD, pady=CONTENT_PAD)

        # Header
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 16))
        section_title(header, "📄  Invoices").pack(side=tk.LEFT)
        make_button(header, "+ Generate Invoice", self._open_generate_dialog).pack(side=tk.RIGHT)

        # Summary strip
        total_income = self._svc.get_total_income()
        pending = self._svc.get_pending()
        summary = tk.Frame(self, bg=BG_DARK)
        summary.pack(fill=tk.X, pady=(0, 12))
        for label, value, color in [
            ("Total Income", format_currency(total_income), ACCENT_2),
            ("Pending Invoices", str(len(pending)), WARNING),
            ("Pending Amount", format_currency(sum(i.amount for i in pending)), WARNING),
        ]:
            card = tk.Frame(summary, bg=BG_CARD, padx=16, pady=10)
            card.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
            tk.Label(card, text=label, font=FONT_SMALL, bg=BG_CARD, fg=FG_SECONDARY).pack(anchor="w")
            tk.Label(card, text=value, font=FONT_H2, bg=BG_CARD, fg=color).pack(anchor="w")

        # Treeview
        cols = ["ID", "Invoice #", "Client", "Project", "Amount", "Issue Date", "Due Date", "Status"]
        tree_frame, self._tree = make_scrolled_tree(self, cols, heights=18)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        for col, w in zip(cols, [30, 120, 130, 150, 100, 100, 100, 90]):
            self._tree.column(col, width=w)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # Action bar
        actions = tk.Frame(self, bg=BG_DARK, pady=8)
        actions.pack(fill=tk.X)
        self._view_btn = make_button(actions, "👁  View", self._open_detail_dialog)
        self._view_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._paid_btn = make_button(actions, "✔ Mark Paid", self._mark_paid, color=SUCCESS)
        self._paid_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._del_btn = make_danger_button(actions, "🗑 Delete", self._delete_invoice)
        self._del_btn.pack(side=tk.LEFT)

        self._tree.bind("<Double-1>", lambda e: self._open_detail_dialog())

        self._load_invoices()

    def _load_invoices(self) -> None:
        for row in self._tree.get_children():
            self._tree.delete(row)
        clients = {c.id: c.full_name for c in self._client_svc.get_all()}
        projects = {p.project_id: p.title for p in self._project_svc.get_all_projects()}
        for inv in self._svc.get_all():
            self._tree.insert("", tk.END, iid=str(inv.invoice_id), values=(
                inv.invoice_id,
                inv.invoice_number,
                clients.get(inv.client_id, "N/A"),
                projects.get(inv.project_id, "N/A"),
                format_currency(inv.amount),
                inv.issue_date,
                inv.due_date,
                inv.status.upper(),
            ))

    def _on_select(self, event) -> None:
        sel = self._tree.selection()
        if sel:
            inv_id = int(sel[0])
            from src.repositories.invoice_repository import InvoiceRepository
            self._selected = InvoiceRepository().find_by_id(inv_id)

    def _open_detail_dialog(self) -> None:
        if not self._selected:
            messagebox.showinfo("Select", "Select an invoice first.", parent=self)
            return
        InvoiceDetailDialog(self, self._selected, self._svc, on_refresh=self._load_invoices)

    def _mark_paid(self) -> None:
        if not self._selected:
            messagebox.showinfo("Select", "Select an invoice first.", parent=self)
            return
        try:
            self._svc.mark_paid(self._selected.invoice_id)
            self._load_invoices()
            messagebox.showinfo("Paid", f"Invoice {self._selected.invoice_number} marked as paid.", parent=self)
        except InvoiceAlreadyPaidException as exc:
            messagebox.showwarning("Already Paid", str(exc), parent=self)
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    def _delete_invoice(self) -> None:
        if not self._selected:
            messagebox.showinfo("Select", "Select an invoice first.", parent=self)
            return
        if confirm_dialog(self, "Delete", f"Delete invoice '{self._selected.invoice_number}'?"):
            try:
                self._svc.delete(self._selected.invoice_id)
                self._selected = None
                self._load_invoices()
            except Exception as exc:
                messagebox.showerror("Error", str(exc), parent=self)

    def _open_generate_dialog(self) -> None:
        InvoiceGenerateDialog(self, self._client_svc, self._project_svc,
                              self._svc, on_save=self._load_invoices)

    def refresh(self) -> None:
        self._load_invoices()


# ====================================================================== #
# Generate dialog
# ====================================================================== #

class InvoiceGenerateDialog(tk.Toplevel):
    """Modal for generating a new invoice."""

    def __init__(self, parent, client_svc: ClientService,
                 project_svc: ProjectService, invoice_svc: InvoiceService, on_save) -> None:
        super().__init__(parent)
        self.title("Generate Invoice")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.wait_visibility()
        self.grab_set()
        self._on_save = on_save
        self._client_svc = client_svc
        self._project_svc = project_svc
        self._invoice_svc = invoice_svc

        w, h = 460, 460
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._clients = client_svc.get_all()
        self._projects = project_svc.get_all_projects()
        self._client_var = tk.StringVar()
        self._project_var = tk.StringVar()
        self._amount_var = tk.StringVar(value="0")
        self._due_days_var = tk.StringVar(value="30")
        self._inv_num_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        body = tk.Frame(self, bg=BG_DARK, padx=28, pady=20)
        body.pack(fill=tk.BOTH, expand=True)
        tk.Label(body, text="Generate Invoice", font=FONT_H2,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 14))

        # Client
        c_row = tk.Frame(body, bg=BG_DARK)
        c_row.pack(fill=tk.X, pady=4)
        tk.Label(c_row, text="Client *", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        self._client_combo = make_combobox(
            c_row, [f"{c.id}: {c.full_name}" for c in self._clients], self._client_var)
        self._client_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Project
        p_row = tk.Frame(body, bg=BG_DARK)
        p_row.pack(fill=tk.X, pady=4)
        tk.Label(p_row, text="Project *", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        self._project_combo = make_combobox(
            p_row, [f"{p.project_id}: {p.title}" for p in self._projects], self._project_var)
        self._project_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        field_row(body, "Invoice # (leave blank=auto)", self._inv_num_var, bg=BG_DARK)
        field_row(body, "Amount (0=auto-calculate)", self._amount_var, bg=BG_DARK)
        field_row(body, "Due in (days)", self._due_days_var, bg=BG_DARK)

        # Preview button and label
        preview_frame = tk.Frame(body, bg=BG_DARK)
        preview_frame.pack(fill=tk.X, pady=4)
        make_button(preview_frame, "🔍 Preview Amount", self._preview, width=15).pack(side=tk.LEFT)
        self._preview_lbl = tk.Label(preview_frame, text="", font=FONT_SMALL, bg=BG_DARK, fg=SUCCESS, justify="left")
        self._preview_lbl.pack(side=tk.LEFT, padx=10)

        tk.Label(body,
                 text="Amount=0 will use the project's billing strategy to calculate.",
                 font=FONT_SMALL, bg=BG_DARK, fg=FG_MUTED, wraplength=380).pack(anchor="w", pady=(4, 12))

        make_button(body, "Generate", self._generate, width=20).pack()


    def _generate(self) -> None:
        client_str = self._client_combo.get()
        project_str = self._project_combo.get()
        if not client_str or not project_str:
            messagebox.showwarning("Validation", "Please select a client and project.", parent=self)
            return
        try:
            client_id = int(client_str.split(":")[0])
            project_id = int(project_str.split(":")[0])
            amount = float(self._amount_var.get() or 0)
            due_days = int(self._due_days_var.get() or 30)
            inv_num = self._inv_num_var.get().strip()
            self._invoice_svc.generate_invoice(
                project_id=project_id,
                client_id=client_id,
                invoice_number=inv_num or "",
                amount=amount,
                due_days=due_days,
            )
            self._on_save()
            self.destroy()
        except DuplicateInvoiceException as exc:
            messagebox.showwarning("Duplicate", str(exc), parent=self)
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    def _preview(self) -> None:
        project_str = self._project_combo.get()
        if not project_str:
            messagebox.showwarning("Validation", "Please select a project.", parent=self)
            return
        try:
            project_id = int(project_str.split(":")[0])
            strat, exp, total = self._invoice_svc.preview_amount(project_id)
            self._preview_lbl.config(
                text=f"Total: {format_currency(total)} (Strategy: {format_currency(strat)} + Exp: {format_currency(exp)})"
            )
            if not self._amount_var.get() or float(self._amount_var.get()) == 0.0:
                self._amount_var.set(f"{total:.2f}")
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)


# ====================================================================== #
# Invoice Detail Dialog                                                   #
# ====================================================================== #

class InvoiceDetailDialog(tk.Toplevel):
    """Modal dialog displaying invoice details and calculation breakdown."""

    def __init__(self, parent, invoice: Invoice, service: InvoiceService, on_refresh) -> None:
        super().__init__(parent)
        self.title(f"Invoice {invoice.invoice_number}")
        self.configure(bg=BG_DARK)
        self.wait_visibility()
        self.grab_set()
        self._invoice = invoice
        self._svc = service
        self._on_refresh = on_refresh

        w, h = 500, 450
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()

    def _build_ui(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        body = tk.Frame(self, bg=BG_DARK, padx=24, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        # Header with actions
        hdr = tk.Frame(body, bg=BG_DARK)
        hdr.pack(fill=tk.X, pady=(0, 16))

        tk.Label(hdr, text="Invoice Details", font=FONT_H2, bg=BG_DARK, fg=FG_PRIMARY).pack(side=tk.LEFT)
        make_danger_button(hdr, "🗑 Delete", self._delete).pack(side=tk.RIGHT, padx=4)
        
        is_pending = self._invoice.status.lower() == "pending"
        pay_btn = make_button(hdr, "✔ Mark Paid", self._mark_paid, color=SUCCESS if is_pending else BG_PANEL)
        pay_btn.pack(side=tk.RIGHT, padx=4)
        if not is_pending:
            pay_btn.config(state=tk.DISABLED)

        # Details Grid
        details = tk.Frame(body, bg=BG_CARD, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER)
        details.pack(fill=tk.X, pady=(0, 20))

        from src.services.client_service import ClientService
        from src.services.project_service import ProjectService
        client = ClientService().get_by_id(self._invoice.client_id)
        project = ProjectService().get_project(self._invoice.project_id)

        info = [
            ("Invoice Number", self._invoice.invoice_number),
            ("Client", client.full_name if client else "N/A"),
            ("Project", project.title if project else "N/A"),
            ("Issue Date", self._invoice.issue_date),
            ("Due Date", self._invoice.due_date),
            ("Status", self._invoice.status.upper()),
            ("Total Amount", format_currency(self._invoice.amount)),
        ]

        for label, val in info:
            row_f = tk.Frame(details, bg=BG_CARD)
            row_f.pack(fill=tk.X, pady=3)
            tk.Label(row_f, text=f"{label}:", font=FONT_SMALL, bg=BG_CARD, fg=FG_SECONDARY, width=18, anchor="w").pack(side=tk.LEFT)
            
            color = FG_PRIMARY
            if label == "Status":
                color = SUCCESS if val == "PAID" else WARNING
            elif label == "Total Amount":
                color = ACCENT
            
            tk.Label(row_f, text=val, font=FONT_BODY, bg=BG_CARD, fg=color).pack(side=tk.LEFT)

        # Breakdown explanation
        if project:
            breakdown = tk.Frame(body, bg=BG_DARK)
            breakdown.pack(fill=tk.X)
            tk.Label(breakdown, text="Calculation Breakdown Preview:", font=FONT_H3, bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 4))
            
            strat, exp, total = self._svc.preview_amount(self._invoice.project_id)
            desc = f"• Billing Strategy ({project.billing_type.title()}): {format_currency(strat)}\n• Billable Expenses: {format_currency(exp)}"
            tk.Label(breakdown, text=desc, font=FONT_BODY, bg=BG_DARK, fg=FG_SECONDARY, justify="left", anchor="w").pack(anchor="w")

    def _mark_paid(self) -> None:
        try:
            self._svc.mark_paid(self._invoice.invoice_id)
            self._invoice = self._svc._repo.find_by_id(self._invoice.invoice_id)
            self._on_refresh()
            self._build_ui()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    def _delete(self) -> None:
        if confirm_dialog(self, "Confirm Delete", f"Delete invoice {self._invoice.invoice_number}?"):
            self._svc.delete(self._invoice.invoice_id)
            self._on_refresh()
            self.destroy()

