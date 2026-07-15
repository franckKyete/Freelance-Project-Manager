"""Tasks screen — task management and time tracking."""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from src.services.task_service import TaskService
from src.services.project_service import ProjectService
from src.factories.task_factory import TaskFactory
from src.models.task import Task
from src.gui.theme import (
    BG_DARK, BG_CARD, BG_PANEL, ACCENT, SUCCESS, WARNING, DANGER,
    FG_PRIMARY, FG_SECONDARY, FG_MUTED,
    FONT_H2, FONT_H3, FONT_BODY, FONT_SMALL,
    CONTENT_PAD, CARD_PAD,
)
from src.gui.widgets import (
    make_button, make_danger_button, make_scrolled_tree,
    make_combobox, field_row, section_title, confirm_dialog,
)
from src.utils.validators import format_hours


class TasksFrame(tk.Frame):
    """Task management screen with time tracker."""

    def __init__(self, parent: tk.Frame) -> None:
        super().__init__(parent, bg=BG_DARK)
        self._task_svc = TaskService()
        self._project_svc = ProjectService()
        self._selected_task: Task | None = None
        self._timer_running = False
        self._timer_start: datetime | None = None
        self._timer_id = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.pack(fill=tk.BOTH, expand=True, padx=CONTENT_PAD, pady=CONTENT_PAD)

        # Header
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 12))
        section_title(header, "✅  Tasks").pack(side=tk.LEFT)
        make_button(header, "+ Add Task", self._open_add_dialog).pack(side=tk.RIGHT)

        # Filters row
        filter_row = tk.Frame(self, bg=BG_DARK)
        filter_row.pack(fill=tk.X, pady=(0, 8))
        tk.Label(filter_row, text="Project:", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY).pack(side=tk.LEFT)
        self._projects = self._project_svc.get_all_projects()
        proj_names = ["All Projects"] + [p.title for p in self._projects]
        self._proj_var = tk.StringVar(value="All Projects")
        proj_combo = make_combobox(filter_row, proj_names, self._proj_var, width=24)
        proj_combo.pack(side=tk.LEFT, padx=(4, 16))
        proj_combo.bind("<<ComboboxSelected>>", lambda e: self._load_tasks())

        tk.Label(filter_row, text="Milestone:", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY).pack(side=tk.LEFT)
        self._milestones = []
        self._ms_var = tk.StringVar(value="All Milestones")
        self._ms_combo = make_combobox(filter_row, ["All Milestones"], self._ms_var, width=24)
        self._ms_combo.pack(side=tk.LEFT, padx=4)
        self._ms_combo.bind("<<ComboboxSelected>>", lambda e: self._load_tasks())

        # Split pane: task list + time tracker
        panes = tk.PanedWindow(self, orient=tk.VERTICAL, bg=BG_DARK, sashwidth=4)
        panes.pack(fill=tk.BOTH, expand=True)

        # ── Top: task list ────────────────────────────────────────────
        top = tk.Frame(panes, bg=BG_CARD)
        panes.add(top, minsize=200)

        cols = ["ID", "Title", "Type", "Priority", "Status", "Est. h", "Done h", "%"]
        list_frame, self._tree = make_scrolled_tree(top, cols, heights=12)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        for col, w in zip(cols, [30, 220, 80, 70, 90, 60, 60, 50]):
            self._tree.column(col, width=w)
        self._tree.bind("<<TreeviewSelect>>", self._on_task_select)

        action_bar = tk.Frame(top, bg=BG_CARD, pady=4)
        action_bar.pack(fill=tk.X, padx=4)
        make_button(action_bar, "✔ Complete", self._complete_task).pack(side=tk.LEFT, padx=2)
        make_danger_button(action_bar, "🗑 Delete", self._delete_task).pack(side=tk.LEFT, padx=2)

        # ── Bottom: time tracker ──────────────────────────────────────
        bottom = tk.Frame(panes, bg=BG_DARK, padx=CARD_PAD, pady=CARD_PAD)
        panes.add(bottom, minsize=180)

        timer_card = tk.Frame(bottom, bg=BG_CARD, padx=CARD_PAD, pady=CARD_PAD)
        timer_card.pack(fill=tk.X, pady=(0, 12))
        tk.Label(timer_card, text="⏱  Time Tracker", font=FONT_H3,
                 bg=BG_CARD, fg=FG_PRIMARY).pack(anchor="w")
        self._timer_label = tk.Label(timer_card, text="00:00:00", font=("Courier New", 28, "bold"),
                                     bg=BG_CARD, fg=ACCENT)
        self._timer_label.pack(pady=6)
        self._task_label = tk.Label(timer_card, text="No task selected",
                                    font=FONT_SMALL, bg=BG_CARD, fg=FG_MUTED)
        self._task_label.pack()

        btn_row = tk.Frame(timer_card, bg=BG_CARD)
        btn_row.pack(pady=8)
        self._start_btn = make_button(btn_row, "▶ Start", self._start_timer, color=SUCCESS)
        self._start_btn.pack(side=tk.LEFT, padx=4)
        self._stop_btn = make_button(btn_row, "■ Stop", self._stop_timer, color=DANGER)
        self._stop_btn.pack(side=tk.LEFT, padx=4)
        self._stop_btn.config(state=tk.DISABLED)

        # Time entries list
        tk.Label(bottom, text="Time Entries", font=FONT_H3,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(4, 4))
        te_cols = ["ID", "Start", "End", "Duration"]
        te_frame, self._te_tree = make_scrolled_tree(bottom, te_cols, heights=4)
        te_frame.pack(fill=tk.X)
        for col, w in zip(te_cols, [30, 180, 180, 100]):
            self._te_tree.column(col, width=w)

        self._load_tasks()

    # ------------------------------------------------------------------ #
    # Data
    # ------------------------------------------------------------------ #

    def _load_tasks(self) -> None:
        for row in self._tree.get_children():
            self._tree.delete(row)

        proj_name = self._proj_var.get()
        selected_proj = next((p for p in self._projects if p.title == proj_name), None)

        # Update milestone dropdown
        if selected_proj:
            self._milestones = self._project_svc.get_milestones(selected_proj.project_id)
            ms_names = ["All Milestones"] + [m.title for m in self._milestones]
        else:
            self._milestones = []
            ms_names = ["All Milestones"]
        self._ms_combo.config(values=ms_names)
        self._ms_var.set("All Milestones")

        ms_name = self._ms_var.get()
        selected_ms = next((m for m in self._milestones if m.title == ms_name), None)

        if selected_ms:
            milestones_to_show = [selected_ms]
        elif selected_proj:
            milestones_to_show = self._milestones
        else:
            # All projects, all milestones
            milestones_to_show = []
            for p in self._projects:
                milestones_to_show.extend(self._project_svc.get_milestones(p.project_id))

        for ms in milestones_to_show:
            for task in self._task_svc.get_tasks_for_milestone(ms.milestone_id):
                progress = task.get_progress()
                self._tree.insert("", tk.END, iid=str(task.task_id), values=(
                    task.task_id, task.title, task.TASK_TYPE.title(),
                    task.priority.title(), task.status.replace("_", " ").title(),
                    f"{task.estimated_hours:.1f}", f"{task.completed_hours:.1f}",
                    f"{progress*100:.0f}%",
                ))

    def _on_task_select(self, event) -> None:
        sel = self._tree.selection()
        if sel:
            task_id = int(sel[0])
            self._selected_task = self._task_svc._task_repo.find_by_id(task_id)
            if self._selected_task:
                self._task_label.config(text=f"Task: {self._selected_task.title}")
                self._load_time_entries()

    def _load_time_entries(self) -> None:
        for row in self._te_tree.get_children():
            self._te_tree.delete(row)
        if not self._selected_task:
            return
        entries = self._task_svc.get_time_entries(self._selected_task.task_id)
        for e in entries:
            self._te_tree.insert("", tk.END, values=(
                e.entry_id, e.start_time, e.end_time, format_hours(e.duration),
            ))

    # ------------------------------------------------------------------ #
    # Timer
    # ------------------------------------------------------------------ #

    def _start_timer(self) -> None:
        if not self._selected_task:
            messagebox.showinfo("No Task", "Select a task before starting the timer.", parent=self)
            return
        if not self._timer_running:
            self._timer_running = True
            self._timer_start = datetime.now()
            self._start_btn.config(state=tk.DISABLED)
            self._stop_btn.config(state=tk.NORMAL)
            self._tick()

    def _tick(self) -> None:
        if self._timer_running:
            elapsed = datetime.now() - self._timer_start
            h, rem = divmod(int(elapsed.total_seconds()), 3600)
            m, s = divmod(rem, 60)
            self._timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
            self._timer_id = self.after(1000, self._tick)

    def _stop_timer(self) -> None:
        if self._timer_running:
            self._timer_running = False
            if self._timer_id:
                self.after_cancel(self._timer_id)
            end = datetime.now()
            start_str = self._timer_start.strftime("%Y-%m-%d %H:%M:%S")
            end_str = end.strftime("%Y-%m-%d %H:%M:%S")
            try:
                self._task_svc.log_time(self._selected_task.task_id, start_str, end_str)
                self._load_time_entries()
                self._load_tasks()
            except Exception as exc:
                messagebox.showerror("Error", str(exc), parent=self)
            self._timer_label.config(text="00:00:00")
            self._start_btn.config(state=tk.NORMAL)
            self._stop_btn.config(state=tk.DISABLED)

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #

    def _open_add_dialog(self) -> None:
        TaskFormDialog(self, self._project_svc, self._task_svc,
                       on_save=lambda: self._load_tasks())

    def _complete_task(self) -> None:
        if not self._selected_task:
            messagebox.showinfo("Select", "Select a task first.", parent=self)
            return
        try:
            self._task_svc.complete_task(self._selected_task.task_id)
            self._load_tasks()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    def _delete_task(self) -> None:
        if not self._selected_task:
            messagebox.showinfo("Select", "Select a task first.", parent=self)
            return
        if confirm_dialog(self, "Delete", f"Delete task '{self._selected_task.title}'?"):
            try:
                self._task_svc.delete_task(self._selected_task.task_id)
                self._selected_task = None
                self._load_tasks()
            except Exception as exc:
                messagebox.showerror("Error", str(exc), parent=self)

    def refresh(self) -> None:
        self._projects = self._project_svc.get_all_projects()
        proj_names = ["All Projects"] + [p.title for p in self._projects]
        self._proj_var.set("All Projects")
        self._load_tasks()


# ====================================================================== #
# Task form dialog
# ====================================================================== #

class TaskFormDialog(tk.Toplevel):
    """Modal for creating a new task."""

    def __init__(self, parent, project_svc: ProjectService,
                 task_svc: TaskService, on_save) -> None:
        super().__init__(parent)
        self.title("New Task")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.grab_set()
        self._task_svc = task_svc
        self._project_svc = project_svc
        self._on_save = on_save

        w, h = 500, 520
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._vars = {k: tk.StringVar() for k in
                      ["title", "description", "estimated_hours", "priority",
                       "task_type", "programming_language", "api_type",
                       "software_used", "word_target"]}
        self._vars["priority"].set("medium")
        self._vars["task_type"].set("development")
        self._vars["programming_language"].set("Python")
        self._vars["api_type"].set("REST")
        self._vars["software_used"].set("Figma")
        self._vars["estimated_hours"].set("0")

        self._projects = project_svc.get_all_projects()
        self._milestones = []
        self._ms_var = tk.StringVar()
        self._proj_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        body = tk.Frame(self, bg=BG_DARK, padx=28, pady=20)
        body.pack(fill=tk.BOTH, expand=True)
        tk.Label(body, text="New Task", font=FONT_H2,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 12))

        # Project + Milestone
        p_row = tk.Frame(body, bg=BG_DARK)
        p_row.pack(fill=tk.X, pady=4)
        tk.Label(p_row, text="Project", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        proj_names = [p.title for p in self._projects]
        self._proj_combo = make_combobox(p_row, proj_names, self._proj_var)
        self._proj_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._proj_combo.bind("<<ComboboxSelected>>", self._update_milestones)

        ms_row = tk.Frame(body, bg=BG_DARK)
        ms_row.pack(fill=tk.X, pady=4)
        tk.Label(ms_row, text="Milestone", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        self._ms_combo = make_combobox(ms_row, [], self._ms_var)
        self._ms_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        field_row(body, "Title *", self._vars["title"], bg=BG_DARK)
        field_row(body, "Description", self._vars["description"], bg=BG_DARK)
        field_row(body, "Estimated Hours", self._vars["estimated_hours"], bg=BG_DARK)

        # Task type
        type_row = tk.Frame(body, bg=BG_DARK)
        type_row.pack(fill=tk.X, pady=4)
        tk.Label(type_row, text="Task Type", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        make_combobox(type_row, TaskFactory.available_types(), self._vars["task_type"]
                      ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Priority
        pri_row = tk.Frame(body, bg=BG_DARK)
        pri_row.pack(fill=tk.X, pady=4)
        tk.Label(pri_row, text="Priority", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        make_combobox(pri_row, ["low", "medium", "high", "critical"],
                      self._vars["priority"]).pack(side=tk.LEFT, fill=tk.X, expand=True)

        field_row(body, "Programming Language", self._vars["programming_language"], bg=BG_DARK)

        from src.models.task import BackendDevelopmentTask
        api_row = tk.Frame(body, bg=BG_DARK)
        api_row.pack(fill=tk.X, pady=4)
        tk.Label(api_row, text="API Type (backend)", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_SECONDARY, width=22, anchor="w").pack(side=tk.LEFT)
        make_combobox(api_row, list(BackendDevelopmentTask.API_TYPES),
                      self._vars["api_type"]).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Frame(body, bg=BG_DARK, height=8).pack()
        make_button(body, "Save Task", self._save, width=20).pack()

    def _update_milestones(self, event=None) -> None:
        proj_name = self._proj_var.get()
        proj = next((p for p in self._projects if p.title == proj_name), None)
        if proj:
            self._milestones = self._project_svc.get_milestones(proj.project_id)
            ms_names = [m.title for m in self._milestones]
            self._ms_combo.config(values=ms_names)
            if ms_names:
                self._ms_combo.current(0)

    def _save(self) -> None:
        title = self._vars["title"].get().strip()
        if not title:
            messagebox.showwarning("Validation", "Title required.", parent=self)
            return
        ms_name = self._ms_var.get()
        ms = next((m for m in self._milestones if m.title == ms_name), None)
        if not ms:
            messagebox.showwarning("Validation", "Please select a milestone.", parent=self)
            return
        task_type = self._vars["task_type"].get()
        try:
            kwargs = dict(
                title=title,
                description=self._vars["description"].get(),
                estimated_hours=float(self._vars["estimated_hours"].get() or 0),
                priority=self._vars["priority"].get(),
            )
            if task_type in ("development", "backend"):
                kwargs["programming_language"] = self._vars["programming_language"].get() or "Python"
            if task_type == "backend":
                kwargs["api_type"] = self._vars["api_type"].get() or "REST"
            self._task_svc.create_task(task_type, ms.milestone_id, **kwargs)
            self._on_save()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)
