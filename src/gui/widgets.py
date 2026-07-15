"""Reusable GUI widget helpers."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from src.gui.theme import (
    BG_CARD, BG_PANEL, ACCENT, ACCENT_HOVER, DANGER,
    FG_PRIMARY, FG_SECONDARY, FG_MUTED, BORDER,
    FONT_H2, FONT_H3, FONT_BODY, FONT_SMALL, SUCCESS,
    STATUS_COLORS,
)


def make_label(parent, text: str, font=FONT_BODY,
               fg=FG_PRIMARY, bg=None, **kwargs) -> tk.Label:
    """Create a consistently styled Label."""
    bg = bg or parent.cget("bg")
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)


def make_button(parent, text: str, command: Callable,
                color=ACCENT, width=None, **kwargs) -> tk.Button:
    """Create a styled flat Button."""
    btn = tk.Button(
        parent, text=text, command=command,
        font=FONT_SMALL, bg=color, fg=FG_PRIMARY,
        activebackground=ACCENT_HOVER, activeforeground=FG_PRIMARY,
        relief="flat", cursor="hand2", padx=10, pady=5,
        width=width or 0, **kwargs,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT_HOVER if color == ACCENT else color))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def make_danger_button(parent, text: str, command: Callable) -> tk.Button:
    """Create a red danger-styled button."""
    return make_button(parent, text, command, color=DANGER)


def make_entry(parent, textvariable: tk.StringVar = None,
               width: int = 30, **kwargs) -> tk.Entry:
    """Create a consistently styled Entry field."""
    return tk.Entry(
        parent,
        textvariable=textvariable,
        font=FONT_BODY,
        bg=BG_CARD,
        fg=FG_PRIMARY,
        insertbackground=FG_PRIMARY,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        width=width,
        **kwargs,
    )


def make_combobox(parent, values: List[str],
                  textvariable: tk.StringVar = None, **kwargs) -> ttk.Combobox:
    """Create a styled read-only Combobox."""
    style = ttk.Style()
    style.configure("App.TCombobox",
                    fieldbackground=BG_CARD,
                    background=BG_CARD,
                    foreground=FG_PRIMARY,
                    selectbackground=ACCENT)
    return ttk.Combobox(
        parent,
        values=values,
        textvariable=textvariable,
        state="readonly",
        font=FONT_BODY,
        style="App.TCombobox",
        **kwargs,
    )


def make_treeview(parent, columns: List[str],
                  heights: int = 15, show_heading=True) -> ttk.Treeview:
    """Create a dark-themed Treeview.

    Args:
        parent: Parent widget.
        columns: List of column id strings.
        heights: Number of visible rows.
        show_heading: Whether to display column headers.

    Returns:
        Configured ttk.Treeview instance.
    """
    style = ttk.Style()
    style.configure("App.Treeview",
                    background=BG_CARD,
                    foreground=FG_PRIMARY,
                    fieldbackground=BG_CARD,
                    rowheight=28,
                    font=FONT_BODY)
    style.configure("App.Treeview.Heading",
                    background=BG_PANEL,
                    foreground=FG_SECONDARY,
                    font=FONT_SMALL,
                    relief="flat")
    style.map("App.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", FG_PRIMARY)])

    show = "headings" if show_heading else "tree"
    tree = ttk.Treeview(
        parent,
        columns=columns,
        show=show,
        height=heights,
        style="App.Treeview",
        selectmode="browse",
    )
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="w", minwidth=60)
    return tree


def make_scrolled_tree(parent, columns: List[str], heights: int = 15) -> tuple:
    """Create a Treeview with a vertical scrollbar.

    Returns:
        Tuple of (frame, treeview) where frame contains both widgets.
    """
    frame = tk.Frame(parent, bg=BG_CARD)
    tree = make_treeview(frame, columns, heights)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    return frame, tree


def section_title(parent, text: str) -> tk.Label:
    """Create a section header label."""
    label = tk.Label(parent, text=text, font=FONT_H2,
                     bg=parent.cget("bg"), fg=FG_PRIMARY, anchor="w")
    return label


def status_badge(parent, status: str) -> tk.Label:
    """Create a small coloured status label."""
    color = STATUS_COLORS.get(status.lower(), FG_MUTED)
    return tk.Label(
        parent, text=f"  {status.upper()}  ",
        font=FONT_SMALL, bg=color, fg="#ffffff",
        padx=4, pady=2,
    )


def field_row(parent, label: str, var: tk.StringVar,
              bg: str = None, entry_width: int = 35) -> tk.Entry:
    """Create a label + entry row and return the Entry widget."""
    bg = bg or parent.cget("bg")
    row = tk.Frame(parent, bg=bg)
    row.pack(fill=tk.X, pady=4)
    tk.Label(row, text=label, font=FONT_SMALL, bg=bg, fg=FG_SECONDARY,
             width=22, anchor="w").pack(side=tk.LEFT)
    entry = make_entry(row, textvariable=var, width=entry_width)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
    return entry


def confirm_dialog(parent, title: str, message: str) -> bool:
    """Show a simple yes/no confirmation dialog.

    Returns:
        True if user confirmed, False otherwise.
    """
    from tkinter import messagebox
    return messagebox.askyesno(title, message, parent=parent)
