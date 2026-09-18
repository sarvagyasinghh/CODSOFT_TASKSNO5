import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

DATA_FILE = "tasks.json"
PRIORITIES = ["Low", "Medium", "High"]
PRIORITY_COLORS = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}


class Task:
    def __init__(self, title, priority="Medium", due_date="", done=False, task_id=None):
        self.id = task_id or datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.title = title
        self.priority = priority
        self.due_date = due_date
        self.done = done

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "due_date": self.due_date,
            "done": self.done,
        }

    @staticmethod
    def from_dict(d):
        return Task(d["title"], d.get("priority", "Medium"), d.get("due_date", ""),
                    d.get("done", False), d.get("id"))


class TaskStore:
    """Handles loading and saving tasks to a JSON file."""

    def __init__(self, path=DATA_FILE):
        self.path = path
        self.tasks = []
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.tasks = [Task.from_dict(d) for d in raw]
            except (json.JSONDecodeError, OSError):
                self.tasks = []
        else:
            self.tasks = []

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)

    def add(self, task):
        self.tasks.append(task)
        self.save()

    def update(self, task_id, **changes):
        for t in self.tasks:
            if t.id == task_id:
                for k, v in changes.items():
                    setattr(t, k, v)
                break
        self.save()

    def delete(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save()

    def get(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("640x520")
        self.minsize(560, 440)
        self.configure(bg="#f5f5f5")

        self.store = TaskStore()
        self.filter_var = tk.StringVar(value="All")
        self.search_var = tk.StringVar()

        self._build_ui()
        self._refresh_list()

    # ---------- UI construction ----------
    def _build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # --- Top: entry bar for adding new tasks ---
        top = tk.Frame(self, bg="#f5f5f5", padx=10, pady=10)
        top.pack(fill="x")

        self.title_entry = ttk.Entry(top, font=("Segoe UI", 11))
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.title_entry.bind("<Return>", lambda e: self._add_task())

        self.priority_var = tk.StringVar(value="Medium")
        priority_menu = ttk.Combobox(top, textvariable=self.priority_var,
                                      values=PRIORITIES, width=8, state="readonly")
        priority_menu.pack(side="left", padx=(0, 6))

        self.due_entry = ttk.Entry(top, width=12, font=("Segoe UI", 10))
        self.due_entry.insert(0, "YYYY-MM-DD")
        self.due_entry.bind("<FocusIn>", lambda e: self._clear_placeholder())
        self.due_entry.pack(side="left", padx=(0, 6))

        add_btn = ttk.Button(top, text="Add Task", command=self._add_task)
        add_btn.pack(side="left")

        # --- Filter / search bar ---
        bar = tk.Frame(self, bg="#f5f5f5", padx=10)
        bar.pack(fill="x")

        for label in ["All", "Active", "Completed"]:
            rb = ttk.Radiobutton(bar, text=label, value=label,
                                  variable=self.filter_var, command=self._refresh_list)
            rb.pack(side="left", padx=4)

        search_entry = ttk.Entry(bar, textvariable=self.search_var, width=20)
        search_entry.pack(side="right")
        search_entry.bind("<KeyRelease>", lambda e: self._refresh_list())
        tk.Label(bar, text="Search:", bg="#f5f5f5").pack(side="right", padx=(0, 4))

        # --- Task list ---
        list_frame = tk.Frame(self, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True)

        columns = ("done", "title", "priority", "due")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("done", text="✓")
        self.tree.heading("title", text="Task")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("due", text="Due Date")
        self.tree.column("done", width=30, anchor="center")
        self.tree.column("title", width=280, anchor="w")
        self.tree.column("priority", width=80, anchor="center")
        self.tree.column("due", width=100, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._toggle_done())

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y")

        for p, color in PRIORITY_COLORS.items():
            self.tree.tag_configure(p, foreground=color)
        self.tree.tag_configure("done", foreground="#9e9e9e")

        # --- Action buttons ---
        actions = tk.Frame(self, bg="#f5f5f5", padx=10, pady=8)
        actions.pack(fill="x")

        ttk.Button(actions, text="Toggle Complete", command=self._toggle_done).pack(side="left", padx=4)
        ttk.Button(actions, text="Edit", command=self._edit_task).pack(side="left", padx=4)
        ttk.Button(actions, text="Delete", command=self._delete_task).pack(side="left", padx=4)
        ttk.Button(actions, text="Clear Completed", command=self._clear_completed).pack(side="right", padx=4)

        self.status_var = tk.StringVar()
        status_bar = tk.Label(self, textvariable=self.status_var, bg="#eeeeee",
                               anchor="w", padx=10, pady=4)
        status_bar.pack(fill="x", side="bottom")

    def _clear_placeholder(self):
        if self.due_entry.get() == "YYYY-MM-DD":
            self.due_entry.delete(0, tk.END)

    # ---------- Core actions ----------
    def _add_task(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Missing title", "Please enter a task description.")
            return
        due = self.due_entry.get().strip()
        if due == "YYYY-MM-DD":
            due = ""
        elif due and not self._valid_date(due):
            messagebox.showerror("Invalid date", "Please use the format YYYY-MM-DD.")
            return

        task = Task(title, self.priority_var.get(), due)
        self.store.add(task)
        self.title_entry.delete(0, tk.END)
        self.due_entry.delete(0, tk.END)
        self.due_entry.insert(0, "YYYY-MM-DD")
        self._refresh_list()

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return sel[0]

    def _toggle_done(self):
        task_id = self._selected_id()
        if not task_id:
            return
        task = self.store.get(task_id)
        if task:
            self.store.update(task_id, done=not task.done)
            self._refresh_list()

    def _delete_task(self):
        task_id = self._selected_id()
        if not task_id:
            messagebox.showinfo("No selection", "Select a task to delete.")
            return
        if messagebox.askyesno("Confirm delete", "Delete the selected task?"):
            self.store.delete(task_id)
            self._refresh_list()

    def _edit_task(self):
        task_id = self._selected_id()
        if not task_id:
            messagebox.showinfo("No selection", "Select a task to edit.")
            return
        task = self.store.get(task_id)
        if not task:
            return

        new_title = simpledialog.askstring("Edit Task", "Task description:", initialvalue=task.title)
        if new_title is None:
            return
        new_title = new_title.strip()
        if not new_title:
            messagebox.showwarning("Invalid", "Task description cannot be empty.")
            return

        new_due = simpledialog.askstring("Edit Task", "Due date (YYYY-MM-DD, blank for none):",
                                          initialvalue=task.due_date)
        if new_due is None:
            new_due = task.due_date
        new_due = new_due.strip()
        if new_due and not self._valid_date(new_due):
            messagebox.showerror("Invalid date", "Please use the format YYYY-MM-DD.")
            return

        self.store.update(task_id, title=new_title, due_date=new_due)
        self._refresh_list()

    def _clear_completed(self):
        completed = [t for t in self.store.tasks if t.done]
        if not completed:
            return
        if messagebox.askyesno("Confirm", f"Remove {len(completed)} completed task(s)?"):
            self.store.tasks = [t for t in self.store.tasks if not t.done]
            self.store.save()
            self._refresh_list()

    @staticmethod
    def _valid_date(s):
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # ---------- Rendering ----------
    def _refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filt = self.filter_var.get()
        query = self.search_var.get().strip().lower()

        visible = self.store.tasks
        if filt == "Active":
            visible = [t for t in visible if not t.done]
        elif filt == "Completed":
            visible = [t for t in visible if t.done]
        if query:
            visible = [t for t in visible if query in t.title.lower()]

        # Sort: incomplete first, then by priority (High > Medium > Low), then due date
        priority_rank = {"High": 0, "Medium": 1, "Low": 2}
        visible.sort(key=lambda t: (t.done, priority_rank.get(t.priority, 1), t.due_date or "9999"))

        for t in visible:
            mark = "✔" if t.done else ""
            tag = "done" if t.done else t.priority
            self.tree.insert("", "end", iid=t.id,
                              values=(mark, t.title, t.priority, t.due_date), tags=(tag,))

        total = len(self.store.tasks)
        done = sum(1 for t in self.store.tasks if t.done)
        self.status_var.set(f"{total} task(s) total  •  {done} completed  •  {total - done} remaining")


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()