"""Clients screen — CRUD for client records."""

import tkinter as tk
from tkinter import messagebox

from src.services.client_service import ClientService
from src.models.client import Client
from src.exceptions.app_exceptions import ClientNotFoundException
from src.gui.theme import (
    BG_DARK, BG_PANEL, BG_CARD, ACCENT, DANGER,
    FG_PRIMARY, FG_SECONDARY, FG_MUTED, BORDER,
    FONT_H2, FONT_H3, FONT_BODY, FONT_SMALL,
    CONTENT_PAD, CARD_PAD,
)
from src.gui.widgets import (
    make_button, make_danger_button, make_scrolled_tree,
    field_row, section_title, confirm_dialog,
)


class ClientsFrame(tk.Frame):
    """Client management screen with list and add/edit/delete actions."""

    def __init__(self, parent: tk.Frame) -> None:
        super().__init__(parent, bg=BG_DARK)
        self._svc = ClientService()
        self._selected_client: Client | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.pack(fill=tk.BOTH, expand=True, padx=CONTENT_PAD, pady=CONTENT_PAD)

        # ── Header ────────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 16))
        section_title(header, "👥  Clients").pack(side=tk.LEFT)
        make_button(header, "+ Add Client", self._open_add_dialog).pack(side=tk.RIGHT)

        # ── Treeview ──────────────────────────────────────────────────
        columns = ["ID", "Name", "Company", "Email", "Phone", "Payment"]
        tree_frame, self._tree = make_scrolled_tree(self, columns, heights=20)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        for col, w in zip(columns, [40, 160, 160, 200, 120, 120]):
            self._tree.column(col, width=w, minwidth=40)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Action bar ────────────────────────────────────────────────
        actions = tk.Frame(self, bg=BG_DARK, pady=10)
        actions.pack(fill=tk.X)
        self._edit_btn = make_button(actions, "✏  Edit", self._open_edit_dialog)
        self._edit_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._del_btn = make_danger_button(actions, "🗑  Delete", self._delete_client)
        self._del_btn.pack(side=tk.LEFT)

        self._load_clients()

    # ------------------------------------------------------------------ #
    # Data
    # ------------------------------------------------------------------ #

    def _load_clients(self) -> None:
        """Reload the treeview from the database."""
        for row in self._tree.get_children():
            self._tree.delete(row)
        clients = self._svc.get_all()
        for c in clients:
            self._tree.insert("", tk.END, iid=str(c.id), values=(
                c.id, c.full_name, c.company_name, c.email,
                c.phone, c.preferred_payment_method,
            ))
        self._selected_client = None

    def _on_select(self, event) -> None:
        selection = self._tree.selection()
        if selection:
            client_id = int(selection[0])
            try:
                self._selected_client = self._svc.get_by_id(client_id)
            except ClientNotFoundException:
                self._selected_client = None

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #

    def _open_add_dialog(self) -> None:
        ClientFormDialog(self, title="Add Client", on_save=self._save_client)

    def _open_edit_dialog(self) -> None:
        if not self._selected_client:
            messagebox.showinfo("Select Client", "Please select a client first.", parent=self)
            return
        ClientFormDialog(self, title="Edit Client",
                         client=self._selected_client, on_save=self._save_client)

    def _save_client(self, data: dict) -> None:
        try:
            if data.get("id"):
                client = self._selected_client
                client.full_name = data["full_name"]
                client.email = data["email"]
                client.phone = data["phone"]
                client.company_name = data["company_name"]
                client.address = data["address"]
                client.preferred_payment_method = data["payment"]
                self._svc.update(client)
            else:
                self._svc.create(
                    full_name=data["full_name"],
                    email=data["email"],
                    phone=data["phone"],
                    company_name=data["company_name"],
                    address=data["address"],
                    preferred_payment_method=data["payment"],
                )
            self._load_clients()
        except (ValueError, Exception) as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    def _delete_client(self) -> None:
        if not self._selected_client:
            messagebox.showinfo("Select Client", "Please select a client first.", parent=self)
            return
        if confirm_dialog(self, "Confirm Delete",
                          f"Delete client '{self._selected_client.full_name}'?\n"
                          "All their projects will also be affected."):
            try:
                self._svc.delete(self._selected_client.id)
                self._load_clients()
            except Exception as exc:
                messagebox.showerror("Error", str(exc), parent=self)

    def refresh(self) -> None:
        """Reload data."""
        self._load_clients()


# ====================================================================== #
# Client Form Dialog                                                       #
# ====================================================================== #

class ClientFormDialog(tk.Toplevel):
    """Modal dialog for adding or editing a client."""

    def __init__(self, parent, title: str, on_save, client: Client = None) -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.grab_set()
        self._on_save = on_save
        self._client = client

        # Centre
        w, h = 480, 440
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._vars = {k: tk.StringVar() for k in
                      ["full_name", "email", "phone", "company_name", "address", "payment"]}

        if client:
            self._vars["full_name"].set(client.full_name)
            self._vars["email"].set(client.email)
            self._vars["phone"].set(client.phone)
            self._vars["company_name"].set(client.company_name)
            self._vars["address"].set(client.address)
            self._vars["payment"].set(client.preferred_payment_method)
        else:
            self._vars["payment"].set("Bank Transfer")

        self._build_ui()

    def _build_ui(self) -> None:
        body = tk.Frame(self, bg=BG_DARK, padx=30, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text=self.title(), font=FONT_H2,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 16))

        fields = [
            ("Full Name *", "full_name"),
            ("Email *", "email"),
            ("Phone", "phone"),
            ("Company Name", "company_name"),
            ("Address", "address"),
        ]
        for label, key in fields:
            field_row(body, label, self._vars[key], bg=BG_DARK)

        # Payment method combobox
        pay_row = tk.Frame(body, bg=BG_DARK)
        pay_row.pack(fill=tk.X, pady=4)
        tk.Label(pay_row, text="Payment Method", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        from src.gui.widgets import make_combobox
        combo = make_combobox(pay_row, list(Client.PAYMENT_METHODS), self._vars["payment"])
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Frame(body, bg=BG_DARK, height=16).pack()
        make_button(body, "Save", self._save, width=20).pack()

    def _save(self) -> None:
        data = {k: v.get().strip() for k, v in self._vars.items()}
        if not data["full_name"] or not data["email"]:
            messagebox.showwarning("Validation", "Name and email are required.", parent=self)
            return
        if self._client:
            data["id"] = self._client.id
        self._on_save(data)
        self.destroy()
