"""Projects screen — project list and detail view with milestones/expenses."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from src.services.project_service import ProjectService
from src.services.client_service import ClientService
from src.models.project import Project
from src.gui.theme import (
    BG_DARK, BG_CARD, BG_PANEL, ACCENT, ACCENT_2, DANGER, SUCCESS, WARNING,
    FG_PRIMARY, FG_SECONDARY, FG_MUTED, BORDER,
    FONT_H2, FONT_H3, FONT_BODY, FONT_SMALL,
    CONTENT_PAD, CARD_PAD,
)
from src.gui.widgets import (
    make_button, make_danger_button, make_scrolled_tree, make_entry,
    make_combobox, field_row, section_title, confirm_dialog,
)
from src.utils.validators import format_currency


class ProjectsFrame(tk.Frame):
    """Projects management screen with tabbed detail view."""

    def __init__(self, parent: tk.Frame) -> None:
        super().__init__(parent, bg=BG_DARK)
        self._svc = ProjectService()
        self._client_svc = ClientService()
        self._selected_project: Project | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.pack(fill=tk.BOTH, expand=True, padx=CONTENT_PAD, pady=CONTENT_PAD)

        # Header
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 12))
        section_title(header, "🗂  Projects").pack(side=tk.LEFT)
        make_button(header, "+ New Project", self._open_add_dialog).pack(side=tk.RIGHT)

        # Main panes: list (left) + detail (right)
        panes = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK,
                               sashwidth=4, sashrelief="flat")
        panes.pack(fill=tk.BOTH, expand=True)

        # ── Left: project list ────────────────────────────────────────
        left = tk.Frame(panes, bg=BG_CARD, width=340)
        panes.add(left, minsize=240)

        cols = ["ID", "Title", "Client", "Status", "Budget"]
        list_frame, self._tree = make_scrolled_tree(left, cols, heights=22)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        for col, w in zip(cols, [30, 160, 100, 80, 90]):
            self._tree.column(col, width=w)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        btn_bar = tk.Frame(left, bg=BG_CARD, pady=4)
        btn_bar.pack(fill=tk.X, padx=4)
        make_button(btn_bar, "✏ Edit", self._open_edit_dialog).pack(side=tk.LEFT, padx=2)
        make_danger_button(btn_bar, "🗑 Delete", self._delete_project).pack(side=tk.LEFT, padx=2)

        # ── Right: detail tabs ────────────────────────────────────────
        self._detail = tk.Frame(panes, bg=BG_DARK)
        panes.add(self._detail, minsize=300)
        self._show_placeholder()

        self._load_projects()

    # ------------------------------------------------------------------ #
    # Data loading
    # ------------------------------------------------------------------ #

    def _load_projects(self) -> None:
        for row in self._tree.get_children():
            self._tree.delete(row)
        clients = {c.id: c.full_name for c in self._client_svc.get_all()}
        for proj in self._svc.get_all_projects():
            self._tree.insert("", tk.END, iid=str(proj.project_id), values=(
                proj.project_id,
                proj.title,
                clients.get(proj.client_id, "N/A"),
                proj.status.title(),
                format_currency(proj.budget),
            ))

    def _on_select(self, event) -> None:
        selection = self._tree.selection()
        if selection:
            pid = int(selection[0])
            self._selected_project = self._svc.get_project(pid)
            self._show_detail()

    # ------------------------------------------------------------------ #
    # Detail panel
    # ------------------------------------------------------------------ #

    def _show_placeholder(self) -> None:
        for w in self._detail.winfo_children():
            w.destroy()
        tk.Label(self._detail,
                 text="Select a project to view details →",
                 font=FONT_BODY, bg=BG_DARK, fg=FG_MUTED).pack(expand=True)

    def _show_detail(self) -> None:
        proj = self._selected_project
        if not proj:
            return
        for w in self._detail.winfo_children():
            w.destroy()

        # Title bar
        title_bar = tk.Frame(self._detail, bg=BG_DARK, pady=8)
        title_bar.pack(fill=tk.X, padx=CARD_PAD)
        tk.Label(title_bar, text=proj.title, font=FONT_H2,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(side=tk.LEFT)

        # Tabs
        nb = ttk.Notebook(self._detail)
        nb.pack(fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=4)

        style = ttk.Style()
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_PANEL,
                        foreground=FG_SECONDARY, font=FONT_SMALL, padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", ACCENT)],
                  foreground=[("selected", FG_PRIMARY)])

        # Overview tab
        overview = tk.Frame(nb, bg=BG_DARK, padx=CARD_PAD, pady=CARD_PAD)
        nb.add(overview, text="Overview")
        self._build_overview(overview, proj)

        # Milestones tab
        ms_tab = tk.Frame(nb, bg=BG_DARK)
        nb.add(ms_tab, text="Milestones")
        self._build_milestones(ms_tab, proj)

        # Expenses tab
        exp_tab = tk.Frame(nb, bg=BG_DARK)
        nb.add(exp_tab, text="Expenses")
        self._build_expenses(exp_tab, proj)

    def _build_overview(self, frame: tk.Frame, proj: Project) -> None:
        info = [
            ("Status", proj.status.title()),
            ("Budget", format_currency(proj.budget)),
            ("Billing", f"{proj.billing_type.title()} @ {format_currency(proj.billing_rate)}"),
            ("Start Date", proj.start_date or "N/A"),
            ("Deadline", proj.deadline or "N/A"),
            ("Progress", f"{proj.calculate_progress()*100:.0f}%"),
        ]
        for label, value in info:
            row = tk.Frame(frame, bg=BG_DARK)
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=label + ":", font=FONT_SMALL,
                     bg=BG_DARK, fg=FG_SECONDARY, width=14, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=value, font=FONT_BODY,
                     bg=BG_DARK, fg=FG_PRIMARY).pack(side=tk.LEFT)

        if proj.description:
            tk.Label(frame, text="Description", font=FONT_SMALL,
                     bg=BG_DARK, fg=FG_SECONDARY).pack(anchor="w", pady=(12, 2))
            tk.Label(frame, text=proj.description, font=FONT_BODY,
                     bg=BG_DARK, fg=FG_PRIMARY, wraplength=400, justify="left").pack(anchor="w")

    def _build_milestones(self, frame: tk.Frame, proj: Project) -> None:
        header = tk.Frame(frame, bg=BG_DARK, padx=CARD_PAD, pady=8)
        header.pack(fill=tk.X)
        tk.Label(header, text="Milestones", font=FONT_H3,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(side=tk.LEFT)
        make_button(header, "+ Add", lambda: self._add_milestone(proj)).pack(side=tk.RIGHT)

        cols = ["ID", "Title", "Due Date", "Status", "Progress"]
        ms_frame, tree = make_scrolled_tree(frame, cols, heights=12)
        ms_frame.pack(fill=tk.BOTH, expand=True, padx=CARD_PAD)
        for col, w in zip(cols, [30, 180, 100, 90, 80]):
            tree.column(col, width=w)

        tree.bind("<Double-1>", lambda e, t=tree, p=proj: self._open_milestone_detail(t, p))

        milestones = self._svc.get_milestones(proj.project_id)
        for m in milestones:
            tree.insert("", tk.END, values=(
                m.milestone_id, m.title, m.due_date or "N/A",
                m.status.title(), f"{m.calculate_progress()*100:.0f}%",
            ))


    def _build_expenses(self, frame: tk.Frame, proj: Project) -> None:
        header = tk.Frame(frame, bg=BG_DARK, padx=CARD_PAD, pady=8)
        header.pack(fill=tk.X)
        tk.Label(header, text="Expenses", font=FONT_H3,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(side=tk.LEFT)
        make_button(header, "+ Add", lambda: self._add_expense(proj)).pack(side=tk.RIGHT)

        cols = ["ID", "Category", "Description", "Amount", "Date", "Billable"]
        exp_frame, tree = make_scrolled_tree(frame, cols, heights=12)
        exp_frame.pack(fill=tk.BOTH, expand=True, padx=CARD_PAD)
        for col, w in zip(cols, [30, 100, 180, 90, 100, 70]):
            tree.column(col, width=w)

        tree.bind("<Double-1>", lambda e, t=tree, p=proj: self._open_expense_detail(t, p))

        expenses = self._svc.get_expenses(proj.project_id)
        total = sum(e.amount for e in expenses)
        for e in expenses:
            tree.insert("", tk.END, values=(
                e.expense_id, e.category, e.description,
                format_currency(e.amount), e.date,
                "Yes" if e.is_billable() else "No",
            ))


        tk.Label(frame, text=f"Total: {format_currency(total)}",
                 font=FONT_H3, bg=BG_DARK, fg=ACCENT_2).pack(anchor="e", padx=CARD_PAD, pady=4)

    # ------------------------------------------------------------------ #
    # CRUD helpers
    # ------------------------------------------------------------------ #

    def _open_add_dialog(self) -> None:
        ProjectFormDialog(self, self._client_svc, on_save=self._save_project)

    def _open_edit_dialog(self) -> None:
        if not self._selected_project:
            messagebox.showinfo("Select", "Select a project first.", parent=self)
            return
        ProjectFormDialog(self, self._client_svc,
                          project=self._selected_project, on_save=self._save_project)

    def _save_project(self, data: dict) -> None:
        try:
            if data.get("id"):
                proj = self._selected_project
                proj.title = data["title"]
                proj.description = data["description"]
                proj.budget = float(data["budget"] or 0)
                proj.start_date = data["start_date"]
                proj.deadline = data["deadline"]
                proj.billing_type = data["billing_type"]
                proj.billing_rate = float(data["billing_rate"] or 0)
                proj.client_id = int(data["client_id"])
                self._svc.update_project(proj)
            else:
                self._svc.create_project(
                    title=data["title"],
                    client_id=int(data["client_id"]),
                    budget=float(data["budget"] or 0),
                    description=data["description"],
                    start_date=data["start_date"],
                    deadline=data["deadline"],
                    billing_type=data["billing_type"],
                    billing_rate=float(data["billing_rate"] or 0),
                )
            self._load_projects()
            self._show_placeholder()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    def _delete_project(self) -> None:
        if not self._selected_project:
            messagebox.showinfo("Select", "Select a project first.", parent=self)
            return
        if confirm_dialog(self, "Delete Project",
                          f"Delete '{self._selected_project.title}' and all its data?"):
            try:
                self._svc.delete_project(self._selected_project.project_id)
                self._selected_project = None
                self._load_projects()
                self._show_placeholder()
            except Exception as exc:
                messagebox.showerror("Error", str(exc), parent=self)

    def _add_milestone(self, proj: Project) -> None:
        MilestoneDialog(self, proj.project_id, self._svc,
                        on_save=lambda: self._show_detail())

    def _add_expense(self, proj: Project) -> None:
        ExpenseDialog(self, proj.project_id, self._svc,
                      on_save=lambda: self._show_detail())

    def _open_milestone_detail(self, tree, project: Project) -> None:
        sel = tree.selection()
        if sel:
            mid = int(sel[0])
            milestones = self._svc.get_milestones(project.project_id)
            ms = next((m for m in milestones if m.milestone_id == mid), None)
            if ms:
                MilestoneDetailDialog(self, ms, project, self._svc, on_refresh=lambda: self._show_detail())

    def _open_expense_detail(self, tree, project: Project) -> None:
        sel = tree.selection()
        if sel:
            eid = int(sel[0])
            expenses = self._svc.get_expenses(project.project_id)
            exp = next((e for e in expenses if e.expense_id == eid), None)
            if exp:
                ExpenseDetailDialog(self, exp, project, self._svc, on_refresh=lambda: self._show_detail())

    def refresh(self) -> None:
        self._load_projects()
        self._show_placeholder()


# ====================================================================== #
# Dialogs                                                                  #
# ====================================================================== #

class ProjectFormDialog(tk.Toplevel):
    """Modal for creating / editing a project."""

    def __init__(self, parent, client_svc: ClientService, on_save, project: Project = None) -> None:
        super().__init__(parent)
        self.title("Edit Project" if project else "New Project")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.wait_visibility()
        self.grab_set()
        self._on_save = on_save
        self._project = project
        self._client_svc = client_svc

        w, h = 500, 540
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._vars = {k: tk.StringVar() for k in
                      ["title", "description", "budget", "start_date", "deadline",
                       "billing_type", "billing_rate", "client_id"]}

        if project:
            self._vars["title"].set(project.title)
            self._vars["description"].set(project.description)
            self._vars["budget"].set(str(project.budget))
            self._vars["start_date"].set(project.start_date)
            self._vars["deadline"].set(project.deadline)
            self._vars["billing_type"].set(project.billing_type)
            self._vars["billing_rate"].set(str(project.billing_rate))
            self._vars["client_id"].set(str(project.client_id))
        else:
            self._vars["start_date"].set(str(date.today()))
            self._vars["billing_type"].set("hourly")

        self._clients = self._client_svc.get_all()
        self._build_ui()

    def _build_ui(self) -> None:
        body = tk.Frame(self, bg=BG_DARK, padx=28, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text=self.title(), font=FONT_H2,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 14))

        field_row(body, "Title *", self._vars["title"], bg=BG_DARK)
        field_row(body, "Description", self._vars["description"], bg=BG_DARK)
        field_row(body, "Budget ($)", self._vars["budget"], bg=BG_DARK)
        field_row(body, "Start Date (YYYY-MM-DD)", self._vars["start_date"], bg=BG_DARK)
        field_row(body, "Deadline (YYYY-MM-DD)", self._vars["deadline"], bg=BG_DARK)

        # Billing type
        bt_row = tk.Frame(body, bg=BG_DARK)
        bt_row.pack(fill=tk.X, pady=4)
        tk.Label(bt_row, text="Billing Type", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        make_combobox(bt_row, ["hourly", "fixed", "retainer"], self._vars["billing_type"]
                      ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        field_row(body, "Billing Rate ($)", self._vars["billing_rate"], bg=BG_DARK)

        # Client picker
        client_row = tk.Frame(body, bg=BG_DARK)
        client_row.pack(fill=tk.X, pady=4)
        tk.Label(client_row, text="Client", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        client_names = [f"{c.id}: {c.full_name}" for c in self._clients]
        self._client_combo = make_combobox(client_row, client_names)
        self._client_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if self._project and self._clients:
            for c in self._clients:
                if c.id == self._project.client_id:
                    self._client_combo.set(f"{c.id}: {c.full_name}")
                    break

        tk.Frame(body, bg=BG_DARK, height=12).pack()
        make_button(body, "Save Project", self._save, width=20).pack()

    def _save(self) -> None:
        title = self._vars["title"].get().strip()
        if not title:
            messagebox.showwarning("Validation", "Title is required.", parent=self)
            return
        client_str = self._client_combo.get()
        client_id = int(client_str.split(":")[0]) if client_str else 0
        data = {k: v.get().strip() for k, v in self._vars.items()}
        data["client_id"] = client_id
        if self._project:
            data["id"] = self._project.project_id
        self._on_save(data)
        self.destroy()


class MilestoneDialog(tk.Toplevel):
    """Simple dialog for adding a milestone to a project."""

    def __init__(self, parent, project_id: int, svc: ProjectService, on_save) -> None:
        super().__init__(parent)
        self.title("Add Milestone")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.wait_visibility()
        self.grab_set()
        self._pid = project_id
        self._svc = svc
        self._on_save = on_save

        self.geometry(f"400x220+{(self.winfo_screenwidth()-400)//2}+{(self.winfo_screenheight()-220)//2}")

        body = tk.Frame(self, bg=BG_DARK, padx=24, pady=20)
        body.pack(fill=tk.BOTH, expand=True)
        tk.Label(body, text="Add Milestone", font=FONT_H2,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 12))
        self._title_var = tk.StringVar()
        self._date_var = tk.StringVar()
        field_row(body, "Title *", self._title_var, bg=BG_DARK)
        field_row(body, "Due Date (YYYY-MM-DD)", self._date_var, bg=BG_DARK)
        make_button(body, "Save", self._save).pack(pady=12)

    def _save(self) -> None:
        title = self._title_var.get().strip()
        if not title:
            messagebox.showwarning("Validation", "Title required.", parent=self)
            return
        try:
            self._svc.add_milestone(self._pid, title, self._date_var.get().strip())
            self._on_save()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)


class ExpenseDialog(tk.Toplevel):
    """Dialog for logging a project expense."""

    def __init__(self, parent, project_id: int, svc: ProjectService, on_save) -> None:
        super().__init__(parent)
        self.title("Add Expense")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.wait_visibility()
        self.grab_set()
        self._pid = project_id
        self._svc = svc
        self._on_save = on_save

        self.geometry(f"420x300+{(self.winfo_screenwidth()-420)//2}+{(self.winfo_screenheight()-300)//2}")

        body = tk.Frame(self, bg=BG_DARK, padx=24, pady=20)
        body.pack(fill=tk.BOTH, expand=True)
        tk.Label(body, text="Add Expense", font=FONT_H2,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 12))

        self._vars = {k: tk.StringVar() for k in ["category", "description", "amount", "date"]}
        self._vars["date"].set(str(date.today()))
        self._vars["category"].set("General")
        self._billable_var = tk.BooleanVar()

        cat_row = tk.Frame(body, bg=BG_DARK)
        cat_row.pack(fill=tk.X, pady=4)
        tk.Label(cat_row, text="Category", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        from src.models.expense import EXPENSE_CATEGORIES
        make_combobox(cat_row, list(EXPENSE_CATEGORIES), self._vars["category"]
                      ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        field_row(body, "Description", self._vars["description"], bg=BG_DARK)
        field_row(body, "Amount ($) *", self._vars["amount"], bg=BG_DARK)
        field_row(body, "Date (YYYY-MM-DD)", self._vars["date"], bg=BG_DARK)

        bill_row = tk.Frame(body, bg=BG_DARK)
        bill_row.pack(fill=tk.X, pady=4)
        tk.Checkbutton(bill_row, text="Billable to client",
                       variable=self._billable_var,
                       bg=BG_DARK, fg=FG_PRIMARY, selectcolor=BG_CARD,
                       activebackground=BG_DARK, font=FONT_SMALL).pack(anchor="w")

        make_button(body, "Save Expense", self._save).pack(pady=8)

    def _save(self) -> None:
        try:
            amount = float(self._vars["amount"].get())
        except ValueError:
            messagebox.showwarning("Validation", "Amount must be a number.", parent=self)
            return
        try:
            self._svc.add_expense(
                project_id=self._pid,
                amount=amount,
                category=self._vars["category"].get(),
                description=self._vars["description"].get().strip(),
                date_str=self._vars["date"].get().strip(),
                billable=self._billable_var.get(),
            )
            self._on_save()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)


# ====================================================================== #
# Milestone Detail Dialog                                                  #
# ====================================================================== #

class MilestoneDetailDialog(tk.Toplevel):
    """Modal dialog displaying milestone details and its tasks."""

    def __init__(self, parent, milestone, project: Project, service: ProjectService, on_refresh) -> None:
        super().__init__(parent)
        self.title(f"Milestone: {milestone.title}")
        self.configure(bg=BG_DARK)
        self.wait_visibility()
        self.grab_set()
        self._milestone = milestone
        self._project = project
        self._svc = service
        self._on_refresh = on_refresh

        w, h = 600, 480
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()

    def _build_ui(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        body = tk.Frame(self, bg=BG_DARK, padx=20, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        hdr = tk.Frame(body, bg=BG_DARK)
        hdr.pack(fill=tk.X, pady=(0, 16))

        tk.Label(hdr, text="Milestone Details", font=FONT_H2, bg=BG_DARK, fg=FG_PRIMARY).pack(side=tk.LEFT)
        make_danger_button(hdr, "🗑 Delete", self._delete).pack(side=tk.RIGHT, padx=4)
        make_button(hdr, "✏ Edit", self._edit).pack(side=tk.RIGHT, padx=4)
        make_button(hdr, "+ Add Task", self._add_task).pack(side=tk.RIGHT, padx=4)

        # Details Card
        details = tk.Frame(body, bg=BG_CARD, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER)
        details.pack(fill=tk.X, pady=(0, 20))

        info = [
            ("Title", self._milestone.title),
            ("Due Date", self._milestone.due_date or "N/A"),
            ("Status", self._milestone.status.title()),
            ("Progress", f"{self._milestone.calculate_progress()*100:.0f}%"),
        ]

        for label, val in info:
            row_f = tk.Frame(details, bg=BG_CARD)
            row_f.pack(fill=tk.X, pady=2)
            tk.Label(row_f, text=f"{label}:", font=FONT_SMALL, bg=BG_CARD, fg=FG_SECONDARY, width=15, anchor="w").pack(side=tk.LEFT)
            tk.Label(row_f, text=val, font=FONT_BODY, bg=BG_CARD, fg=FG_PRIMARY).pack(side=tk.LEFT)

        # Tasks section
        tk.Label(body, text="Tasks", font=FONT_H3, bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 8))
        cols = ["ID", "Title", "Type", "Priority", "Status", "Progress"]
        tree_frame, self._task_tree = make_scrolled_tree(body, cols, heights=6)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        for col, w in zip(cols, [30, 220, 80, 80, 80, 70]):
            self._task_tree.column(col, width=w)

        # Load tasks
        from src.services.task_service import TaskService
        tasks = TaskService().get_tasks_for_milestone(self._milestone.milestone_id)
        for t in tasks:
            self._task_tree.insert("", tk.END, values=(
                t.task_id, t.title, t.TASK_TYPE.title(), t.priority.title(), t.status.replace("_", " ").title(), f"{t.get_progress()*100:.0f}%"
            ))

    def _edit(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Edit Milestone")
        dialog.geometry(f"360x200+{(self.winfo_screenwidth()-360)//2}+{(self.winfo_screenheight()-200)//2}")
        dialog.configure(bg=BG_DARK)
        dialog.wait_visibility()
        dialog.grab_set()

        body = tk.Frame(dialog, bg=BG_DARK, padx=20, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        title_var = tk.StringVar(value=self._milestone.title)
        date_var = tk.StringVar(value=self._milestone.due_date)

        field_row(body, "Title *", title_var, bg=BG_DARK)
        field_row(body, "Due Date (YYYY-MM-DD)", date_var, bg=BG_DARK)

        def save_ms() -> None:
            t = title_var.get().strip()
            if not t:
                messagebox.showwarning("Validation", "Title required.", parent=dialog)
                return
            self._milestone.title = t
            self._milestone.due_date = date_var.get().strip()
            self._svc.update_milestone(self._milestone)
            self._on_refresh()
            self._build_ui()
            dialog.destroy()

        make_button(body, "Save", save_ms).pack(pady=10)

    def _add_task(self) -> None:
        from src.gui.tasks import TaskFormDialog
        from src.services.task_service import TaskService
        
        def on_task_added() -> None:
            self._build_ui()
            self._on_refresh()

        TaskFormDialog(self, self._svc, TaskService(), on_task_added)

    def _delete(self) -> None:
        if confirm_dialog(self, "Confirm Delete", f"Delete milestone '{self._milestone.title}'?"):
            self._svc.delete_milestone(self._milestone.milestone_id)
            self._on_refresh()
            self.destroy()


# ====================================================================== #
# Expense Detail Dialog                                                    #
# ====================================================================== #

class ExpenseDetailDialog(tk.Toplevel):
    """Modal dialog displaying expense details and allowing inline edits/delete."""

    def __init__(self, parent, expense, project: Project, service: ProjectService, on_refresh) -> None:
        super().__init__(parent)
        self.title("Expense Details")
        self.configure(bg=BG_DARK)
        self.wait_visibility()
        self.grab_set()
        self._expense = expense
        self._project = project
        self._svc = service
        self._on_refresh = on_refresh

        w, h = 420, 320
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._vars = {k: tk.StringVar() for k in ["category", "description", "amount", "date"]}
        self._vars["category"].set(expense.category)
        self._vars["description"].set(expense.description)
        self._vars["amount"].set(str(expense.amount))
        self._vars["date"].set(expense.date)
        self._billable_var = tk.BooleanVar(value=expense.is_billable())

        self._build_ui()

    def _build_ui(self) -> None:
        body = tk.Frame(self, bg=BG_DARK, padx=24, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="Edit Expense", font=FONT_H2, bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 12))

        cat_row = tk.Frame(body, bg=BG_DARK)
        cat_row.pack(fill=tk.X, pady=4)
        tk.Label(cat_row, text="Category", font=FONT_SMALL, bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        from src.models.expense import EXPENSE_CATEGORIES
        make_combobox(cat_row, list(EXPENSE_CATEGORIES), self._vars["category"]).pack(side=tk.LEFT, fill=tk.X, expand=True)

        field_row(body, "Description", self._vars["description"], bg=BG_DARK)
        field_row(body, "Amount ($) *", self._vars["amount"], bg=BG_DARK)
        field_row(body, "Date (YYYY-MM-DD)", self._vars["date"], bg=BG_DARK)

        bill_row = tk.Frame(body, bg=BG_DARK)
        bill_row.pack(fill=tk.X, pady=4)
        tk.Checkbutton(bill_row, text="Billable to client", variable=self._billable_var, bg=BG_DARK, fg=FG_PRIMARY, selectcolor=BG_CARD, activebackground=BG_DARK, font=FONT_SMALL).pack(anchor="w")

        btn_row = tk.Frame(body, bg=BG_DARK, pady=10)
        btn_row.pack(fill=tk.X)
        
        make_danger_button(btn_row, "🗑 Delete", self._delete).pack(side=tk.RIGHT, padx=4)
        make_button(btn_row, "Save", self._save).pack(side=tk.RIGHT, padx=4)

    def _save(self) -> None:
        try:
            amount = float(self._vars["amount"].get())
        except ValueError:
            messagebox.showwarning("Validation", "Amount must be a number.", parent=self)
            return
        try:
            self._expense.category = self._vars["category"].get()
            self._expense.description = self._vars["description"].get().strip()
            self._expense.amount = amount
            self._expense.date = self._vars["date"].get().strip()
            self._expense.set_billable(self._billable_var.get())
            
            from src.repositories.expense_repository import ExpenseRepository
            ExpenseRepository().save(self._expense)
            
            self._on_refresh()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    def _delete(self) -> None:
        if confirm_dialog(self, "Confirm Delete", "Delete this expense record?"):
            self._svc.delete_expense(self._expense.expense_id)
            self._on_refresh()
            self.destroy()
