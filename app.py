"""WaterBuddy - Python desktop version of the WaterBuddy hydration tracker.
Run with: python WaterBuddy_Python.py
Uses only Python's standard library (Tkinter, JSON, datetime, pathlib).
"""
import json
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

BG = "#F4F8FF"
NAVY = "#07152F"
BLUE = "#2879FF"
CYAN = "#56DDF4"
INK = "#182B4B"
MUTED = "#8191AA"
GREEN = "#13B887"
WHITE = "#FFFFFF"
LINE = "#E6EDF7"
DATA_FILE = Path.home() / ".waterbuddy_data.json"
DEFAULT_GOALS = {"Child": 1500, "Teen": 2000, "Adult": 2000, "Senior": 1800}

class WaterBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WaterBuddy — Your Daily Hydration Companion")
        self.root.geometry("1040x850")
        self.root.minsize(760, 680)
        self.root.configure(bg=BG)
        self.age_group = "Teen"
        self.goal = DEFAULT_GOALS[self.age_group]
        self.entries = []
        self.day = date.today().isoformat()
        self._build()
        self._load()
        self.refresh()
        self.root.after(60000, self._check_day)

    def _label(self, parent, text, size=10, color=INK, bold=False, **kwargs):
        return tk.Label(parent, text=text, bg=WHITE, fg=color,
                        font=("Arial", size, "bold" if bold else "normal"), **kwargs)

    def _card(self, parent, padx=20, pady=17):
        frame = tk.Frame(parent, bg=WHITE, padx=padx, pady=pady,
                         highlightbackground=LINE, highlightthickness=1)
        frame.pack(fill="x", pady=(0, 14))
        return frame

    def _build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=28, pady=15)
        header.pack(fill="x")
        tk.Label(header, text="💧  WaterBuddy", bg=NAVY, fg=WHITE,
                 font=("Arial", 21, "bold")).pack(side="left")
        tk.Label(header, text="YOUR DAILY HYDRATION COMPANION", bg=NAVY,
                 fg="#9DB8E7", font=("Arial", 9, "bold")).pack(side="left", padx=15)
        self.date_label = tk.Label(header, bg=NAVY, fg="#D8E5F8", font=("Arial", 10))
        self.date_label.pack(side="right")

        hero = tk.Frame(self.root, bg=NAVY, padx=35, pady=25)
        hero.pack(fill="x")
        hero_text = tk.Frame(hero, bg=NAVY)
        hero_text.pack(side="left", fill="x", expand=True)
        tk.Label(hero_text, text="A LITTLE WATER, A BETTER DAY", bg=NAVY,
                 fg=CYAN, font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(hero_text, text="Make hydration\nyour superpower.", bg=NAVY,
                 fg=WHITE, font=("Arial", 30, "bold"), justify="left").pack(anchor="w", pady=8)
        tk.Label(hero_text, text="Track your water, celebrate small wins, and take your day one sip at a time.",
                 bg=NAVY, fg="#C0CEE8", font=("Arial", 11), wraplength=570,
                 justify="left").pack(anchor="w")
        tk.Label(hero, text="💧", bg=NAVY, fg=CYAN, font=("Arial", 65)).pack(side="right", padx=30)

        body = tk.Frame(self.root, bg=BG, padx=22, pady=18)
        body.pack(fill="both", expand=True)
        stats = tk.Frame(body, bg=BG)
        stats.pack(fill="x", pady=(0, 15))
        self.stat_values = []
        for title, color in (("💧 WATER DRUNK", BLUE), ("🎯 REMAINING", INK), ("⚡ COMPLETED", GREEN)):
            card = tk.Frame(stats, bg=WHITE, padx=16, pady=13,
                            highlightbackground=LINE, highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(card, text=title, bg=WHITE, fg=MUTED,
                     font=("Arial", 9, "bold")).pack(anchor="w")
            value = tk.Label(card, text="0", bg=WHITE, fg=color, font=("Arial", 21, "bold"))
            value.pack(anchor="w", pady=(7, 2))
            self.stat_values.append(value)

        columns = tk.Frame(body, bg=BG)
        columns.pack(fill="both", expand=True)
        left = tk.Frame(columns, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 9))
        right = tk.Frame(columns, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(9, 0))

        progress = self._card(left)
        self._label(progress, "Your hydration progress", 16, bold=True).pack(anchor="w")
        self._label(progress, "Watch your bottle fill as you drink.", color=MUTED).pack(anchor="w", pady=(4, 10))
        bottle_row = tk.Frame(progress, bg=WHITE)
        bottle_row.pack(fill="x", pady=5)
        self.bottle = tk.Canvas(bottle_row, width=125, height=205, bg=WHITE, highlightthickness=0)
        self.bottle.pack(side="left", padx=(5, 20))
        bottle_info = tk.Frame(bottle_row, bg=WHITE)
        bottle_info.pack(side="left", fill="x", expand=True)
        self.percent_label = self._label(bottle_info, "0%", 31, BLUE, True)
        self.percent_label.pack(anchor="w")
        self.status_label = self._label(bottle_info, "Fresh start!", 12, bold=True)
        self.status_label.pack(anchor="w", pady=(3, 5))
        self.message_label = self._label(bottle_info, "Every journey begins with one sip.", color=MUTED,
                                         wraplength=210, justify="left")
        self.message_label.pack(anchor="w")
        self.bar = ttk.Progressbar(progress, maximum=100, mode="determinate")
        self.bar.pack(fill="x", pady=(10, 5))
        self.progress_label = self._label(progress, "0 ml consumed   Goal: 2000 ml", 9, MUTED)
        self.progress_label.pack(anchor="w")

        tk.Frame(progress, bg=LINE, height=1).pack(fill="x", pady=14)
        self._label(progress, "Log a drink", 15, bold=True).pack(anchor="w")
        self._label(progress, "Choose an amount to add to today's total.", color=MUTED).pack(anchor="w", pady=(4, 10))
        quick = tk.Frame(progress, bg=WHITE)
        quick.pack(fill="x")
        for amount, icon, name in ((150, "🥛", "Small glass"), (250, "💧", "One glass"), (500, "🫗", "Large bottle")):
            tk.Button(quick, text=f"{icon}\n{amount} ml\n{name}", command=lambda a=amount: self.add_water(a),
                      bg="#EDF5FF", fg=INK, activebackground="#DCEBFF", relief="flat",
                      font=("Arial", 10, "bold"), padx=8, pady=8, cursor="hand2").pack(side="left", expand=True, fill="x", padx=3)
        self._label(progress, "Custom amount (ml)", bold=True).pack(anchor="w", pady=(14, 5))
        custom_row = tk.Frame(progress, bg=WHITE)
        custom_row.pack(fill="x")
        self.custom_entry = tk.Entry(custom_row, font=("Arial", 11), relief="solid", bd=1)
        self.custom_entry.pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(custom_row, text="+ Add water", command=self.add_custom, bg=BLUE, fg=WHITE,
                  activebackground="#1D64DB", relief="flat", font=("Arial", 10, "bold"),
                  padx=12, pady=9, cursor="hand2").pack(side="left", padx=(8, 0))

        history = self._card(left)
        history_head = tk.Frame(history, bg=WHITE)
        history_head.pack(fill="x")
        self._label(history_head, "Today's drink history", 15, bold=True).pack(side="left")
        tk.Button(history_head, text="↶ Undo last", command=self.undo, bg="#F3F7FF", fg=INK,
                  relief="flat", font=("Arial", 9, "bold"), padx=10, pady=6).pack(side="right")
        self.history_frame = tk.Frame(history, bg=WHITE)
        self.history_frame.pack(fill="x", pady=(10, 0))

        settings = self._card(right)
        self._label(settings, "Your daily goal", 16, bold=True).pack(anchor="w")
        self._label(settings, "Choose an age group and set your own tracking target.", color=MUTED).pack(anchor="w", pady=(4, 12))
        self._label(settings, "Age group", bold=True).pack(anchor="w")
        self.age_var = tk.StringVar(value=self.age_group)
        age_select = ttk.Combobox(settings, textvariable=self.age_var, state="readonly",
                                  values=tuple(DEFAULT_GOALS.keys()))
        age_select.pack(fill="x", pady=(5, 12))
        age_select.bind("<<ComboboxSelected>>", self.change_age)
        self._label(settings, "Daily goal (ml)", bold=True).pack(anchor="w")
        goal_row = tk.Frame(settings, bg=WHITE)
        goal_row.pack(fill="x", pady=(5, 5))
        self.goal_entry = tk.Entry(goal_row, font=("Arial", 11), relief="solid", bd=1)
        self.goal_entry.pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(goal_row, text="Save", command=self.save_goal, bg=BLUE, fg=WHITE,
                  relief="flat", font=("Arial", 10, "bold"), padx=16, pady=8).pack(side="left", padx=7)
        self.suggestion = self._label(settings, "Suggested starting point: 2000 ml.", 9, MUTED)
        self.suggestion.pack(anchor="w", pady=(0, 12))
        tk.Frame(settings, bg=LINE, height=1).pack(fill="x", pady=12)
        self.tip_icon = tk.Label(settings, text="🎒", bg="#EAF6FF", font=("Arial", 20), padx=10, pady=8)
        self.tip_icon.pack(side="left", padx=(0, 10))
        tip_text = tk.Frame(settings, bg=WHITE)
        tip_text.pack(side="left", fill="x", expand=True)
        self.tip_title = self._label(tip_text, "Hydration tip", bold=True, wraplength=240, justify="left")
        self.tip_title.pack(anchor="w")
        self.tip_body = self._label(tip_text, "", 9, MUTED, wraplength=250, justify="left")
        self.tip_body.pack(anchor="w", pady=(4, 0))
        self._label(settings, "Hydration needs vary. This tracker is for habit tracking, not medical advice.", 8, MUTED,
                    wraplength=340, justify="left").pack(anchor="w", pady=(14, 0))

        wins = self._card(right)
        self._label(wins, "Little wins ✨", 15, bold=True).pack(anchor="w")
        self.win_icon = tk.Label(wins, text="🌊", bg="#EAF6FF", font=("Arial", 21), padx=10, pady=8)
        self.win_icon.pack(side="left", padx=(0, 10), pady=12)
        win_text = tk.Frame(wins, bg=WHITE)
        win_text.pack(side="left", fill="x", expand=True, pady=12)
        self.win_title = self._label(win_text, "Your journey starts here", bold=True)
        self.win_title.pack(anchor="w")
        self.win_body = self._label(win_text, "Log your first drink to begin.", 9, MUTED, wraplength=245, justify="left")
        self.win_body.pack(anchor="w", pady=(4, 0))
        tk.Button(wins, text="↻ Reset today's tracker", command=self.reset, bg="#F3F7FF", fg=INK,
                  relief="flat", font=("Arial", 10, "bold"), pady=9).pack(fill="x", pady=(10, 4))
        tk.Label(self.root, text="Made with 💙 for healthier everyday habits.  WaterBuddy · Sip smart, feel good.",
                 bg=BG, fg=MUTED, font=("Arial", 9), pady=9).pack()

    def total(self):
        return sum(item["amount"] for item in self.entries)

    def _load(self):
        try:
            if DATA_FILE.exists():
                saved = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                self.age_group = saved.get("age_group", "Teen")
                if self.age_group not in DEFAULT_GOALS:
                    self.age_group = "Teen"
                self.goal = int(saved.get("goal", DEFAULT_GOALS[self.age_group]))
                if not 250 <= self.goal <= 10000:
                    self.goal = DEFAULT_GOALS[self.age_group]
                if saved.get("day") == self.day:
                    self.entries = [e for e in saved.get("entries", []) if 0 < int(e.get("amount", 0)) <= 5000]
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.entries = []

    def _save(self):
        payload = {"day": self.day, "age_group": self.age_group, "goal": self.goal, "entries": self.entries}
        try:
            DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            messagebox.showwarning("Storage", "WaterBuddy could not save data on this computer.")

    def add_water(self, amount):
        if not 1 <= amount <= 5000:
            messagebox.showwarning("Invalid amount", "Enter an amount from 1 to 5,000 ml.")
            return
        self.entries.append({"amount": amount, "time": datetime.now().isoformat(timespec="seconds")})
        self._save()
        self.refresh()

    def add_custom(self):
        try:
            amount = int(self.custom_entry.get())
        except ValueError:
            messagebox.showwarning("Invalid amount", "Please enter a number of millilitres.")
            return
        if not 1 <= amount <= 5000:
            messagebox.showwarning("Invalid amount", "Enter an amount from 1 to 5,000 ml.")
            return
        self.add_water(amount)
        self.custom_entry.delete(0, "end")

    def save_goal(self):
        try:
            value = int(self.goal_entry.get())
        except ValueError:
            value = 0
        if not 250 <= value <= 10000:
            messagebox.showwarning("Invalid goal", "Choose a goal between 250 and 10,000 ml.")
            return
        self.goal = value
        self._save()
        self.refresh()

    def change_age(self, _event=None):
        self.age_group = self.age_var.get()
        self.goal = DEFAULT_GOALS[self.age_group]
        self._save()
        self.refresh()

    def undo(self):
        if not self.entries:
            messagebox.showinfo("Undo", "There is no drink entry to undo yet.")
            return
        self.entries.pop()
        self._save()
        self.refresh()

    def reset(self):
        if messagebox.askyesno("Reset tracker", "Clear today's drink history? Your goal will stay saved."):
            self.entries.clear()
            self._save()
            self.refresh()

    def draw_bottle(self, percent):
        c = self.bottle
        c.delete("all")
        c.create_rectangle(38, 18, 88, 190, fill="#EFF8FF", outline="#C7E2FF", width=4)
        c.create_oval(38, 175, 88, 205, fill="#EFF8FF", outline="#C7E2FF", width=3)
        c.create_rectangle(49, 7, 77, 23, fill="#EFF8FF", outline="#C7E2FF", width=3)
        fill_h = 160 * min(100, percent) / 100
        if fill_h > 0:
            y = 187 - fill_h
            c.create_rectangle(42, y, 84, 187, fill="#45C8F3", outline="")
            c.create_oval(42, y - 5, 84, y + 5, fill="#8DEBFF", outline="")
        c.create_text(63, 105, text="💧", font=("Arial", 22))

    def refresh(self):
        amount = self.total()
        percent = round(amount / self.goal * 100) if self.goal else 0
        remaining = max(0, self.goal - amount)
        self.stat_values[0].config(text=f"{amount:,} ml")
        self.stat_values[1].config(text=f"{remaining:,} ml")
        self.stat_values[2].config(text=f"{percent}%")
        self.percent_label.config(text=f"{percent}%")
        self.progress_label.config(text=f"{amount:,} ml consumed   Goal: {self.goal:,} ml")
        self.bar["value"] = min(100, percent)
        self.date_label.config(text=date.today().strftime("%a, %d %b %Y"))
        self.age_var.set(self.age_group)
        self.goal_entry.delete(0, "end")
        self.goal_entry.insert(0, str(self.goal))
        self.suggestion.config(text=f"Suggested starting point: {DEFAULT_GOALS[self.age_group]:,} ml. Editable target.")
        self.draw_bottle(percent)
        if amount == 0:
            title, msg = "Fresh start!", "Every journey begins with one sip. Let's get started."
            win = ("🌊", "Your journey starts here", "Log your first drink to begin collecting little wins.")
        elif percent < 25:
            title, msg = "Nice beginning!", "Small actions build habits. Keep water nearby."
            win = ("🌱", "First sip logged!", "You've taken the first step.")
        elif percent < 50:
            title, msg = "You're on your way!", "A lovely start. Keep it steady."
            win = ("⭐", "Quarter-way champion!", "You've reached at least 25% of your chosen goal.")
        elif percent < 75:
            title, msg = "Look at you go!", "You've crossed the halfway mark. Keep it comfortable."
            win = ("🏅", "Halfway hero!", "Celebrate your progress.")
        elif percent < 100:
            title, msg = "So close!", f"{remaining:,} ml remaining. No need to rush."
            win = ("🚀", "Final stretch!", "You're at least 75% there. Stay comfortable.")
        else:
            title, msg = "Goal achieved!", "Wonderful! Keep listening to your body's needs."
            win = ("🏆", "Goal reached!", "You reached your selected goal.")
        self.status_label.config(text=title)
        self.message_label.config(text=msg)
        self.win_icon.config(text=win[0])
        self.win_title.config(text=win[1])
        self.win_body.config(text=win[2])
        tips = {
            "Child": ("🧸", "Make water breaks fun", "Keep water nearby during play and study. Ask a trusted adult about your hydration needs."),
            "Teen": ("🎒", "Hydrate around your routine", "Keep a reusable bottle handy during school, study sessions and activities."),
            "Adult": ("🌿", "Build a simple habit", "Pair water breaks with everyday routines, such as meals or desk breaks."),
            "Senior": ("☀️", "Remember regular sips", "Follow any clinician's fluid guidance.")
        }
        tip = tips[self.age_group]
        self.tip_icon.config(text=tip[0])
        self.tip_title.config(text=tip[1])
        self.tip_body.config(text=tip[2])
        self._render_history()

    def _render_history(self):
        for child in self.history_frame.winfo_children():
            child.destroy()
        if not self.entries:
            self._label(self.history_frame, "💧 Your first glass will appear here.", color=MUTED).pack(pady=12)
            return
        for index, entry in enumerate(reversed(self.entries)):
            row = tk.Frame(self.history_frame, bg=WHITE, pady=6)
            row.pack(fill="x")
            tk.Label(row, text="🥛", bg="#EDF6FF", font=("Arial", 15), padx=8, pady=4).pack(side="left")
            info = tk.Frame(row, bg=WHITE)
            info.pack(side="left", padx=10, fill="x", expand=True)
            self._label(info, "Water intake" + (" · Latest" if index == 0 else ""), bold=True).pack(anchor="w")
            try:
                time_text = datetime.fromisoformat(entry["time"]).strftime("%I:%M %p")
            except (KeyError, ValueError):
                time_text = "Time unavailable"
            self._label(info, time_text, 9, MUTED).pack(anchor="w")
            tk.Label(row, text=f"+{entry['amount']} ml", bg=WHITE, fg=BLUE,
                     font=("Arial", 10, "bold")).pack(side="right")

    def _check_day(self):
        today = date.today().isoformat()
        if today != self.day:
            self.day = today
            self.entries = []
            self._save()
            self.refresh()
        self.root.after(60000, self._check_day)

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterBuddyApp(root)
    root.mainloop()
