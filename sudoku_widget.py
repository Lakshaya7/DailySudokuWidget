import tkinter as tk
from tkinter import messagebox
import random
import jsonimport tkinter as tk
from tkinter import messagebox
import random
import json
import os
from datetime import date

class ThemeableSudoku:
    def __init__(self, root):
        self.root = root
        self.root.title("SUDOKU WIDGET")
        
        # --- THEMES ---
        self.themes = {
            "Future Retro": {"bg": "#0d0221", "grid": "#120438", "line": "#ff00ff", "fixed": "#00ffff", "user": "#ffcc00", "btn": "#ea00d9", "font": "Consolas"},
            "Wooden Blocks": {"bg": "#3e2723", "grid": "#5d4037", "line": "#211007", "fixed": "#ffcc80", "user": "#ffffff", "btn": "#ffcc80", "font": "Georgia"},
            "Paper Ink": {"bg": "#f5f5dc", "grid": "#ffffff", "line": "#000000", "fixed": "#000080", "user": "#d32f2f", "btn": "#555555", "font": "Courier"},
            "Midnight OLED": {"bg": "#000000", "grid": "#111111", "line": "#333333", "fixed": "#ffffff", "user": "#00ff00", "btn": "#444444", "font": "Verdana"},
            "Forest Nature": {"bg": "#1b5e20", "grid": "#2e7d32", "line": "#003300", "fixed": "#c8e6c9", "user": "#ffff00", "btn": "#ffffff", "font": "Segoe UI"},
            "Royal Gold": {"bg": "#1a237e", "grid": "#283593", "line": "#ffd700", "fixed": "#ffd700", "user": "#ffffff", "btn": "#ffd700", "font": "Times New Roman"}
        }
        
        self.theme_names = list(self.themes.keys())
        self.current_theme_idx = 0
        
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        self.cache_file = "sudoku_cache.json"
        self.cells = {}
        self.board = []
        self.original_puzzle = []
        
        # Register validation
        self.vcmd = (self.root.register(self.validate_input), '%P')
        
        self.load_or_generate_data()
        self.create_header()
        self.create_grid()
        self.create_controls()
        self.create_status_bar()
        
        self.apply_theme(self.theme_names[0])
        
        screen_w = self.root.winfo_screenwidth()
        # Adjusted height to fit the additional button row
        self.root.geometry(f"340x620+{screen_w - 380}+80")
        
        # Dragging logic
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def validate_input(self, P):
        if P == "" or (P.isdigit() and len(P) == 1 and P != '0'):
            self.root.after(100, self.check_completion)
            return True
        return False

    def set_status(self, message, color=None):
        t = self.themes[self.theme_names[self.current_theme_idx]]
        display_color = color if color else t["line"]
        self.status_label.config(text=message, fg=display_color)

    def check_completion(self):
        current_state = []
        is_full = True
        for r in range(9):
            row = []
            for c in range(9):
                val = self.cells[(r, c)].get()
                if not val:
                    is_full = False
                row.append(int(val) if val else 0)
            current_state.append(row)
        
        if not is_full:
            self.set_status("Playing...")
        else:
            if self.is_board_correct(current_state):
                self.set_status("✨ SOLVED CORRECTLY! ✨", "#00ff00")
            else:
                self.set_status("❌ INCORRECT - TRY AGAIN", "#ff3366")

    def is_board_correct(self, board):
        for i in range(9):
            row_set = {board[i][j] for j in range(9)}
            col_set = {board[j][i] for j in range(9)}
            if len(row_set) < 9 or 0 in row_set: return False
            if len(col_set) < 9 or 0 in col_set: return False
        for r in range(0, 9, 3):
            for c in range(0, 9, 3):
                box = {board[r+i][c+j] for i in range(3) for j in range(3)}
                if len(box) < 9 or 0 in box: return False
        return True

    def apply_theme(self, theme_name):
        t = self.themes[theme_name]
        self.root.configure(bg=t["bg"], highlightbackground=t["line"], highlightthickness=2)
        self.header.config(bg=t["bg"])
        self.header_label.config(bg=t["bg"], fg=t["line"], font=(t["font"], 14, "bold"))
        self.theme_btn.config(bg=t["bg"], fg=t["line"], font=(t["font"], 9, "underline"))
        self.close_btn.config(bg=t["bg"], fg=t["line"], font=(t["font"], 12, "bold"))
        self.outer_grid.config(bg=t["line"])
        self.status_frame.config(bg=t["bg"])
        self.status_label.config(bg=t["bg"], font=(t["font"], 10, "italic"))
        self.set_status("Ready")

        for (r, c), cell in self.cells.items():
            is_orig = self.original_puzzle[r][c] != 0
            bw_x = 3 if (c + 1) % 3 == 0 and c < 8 else 1
            bw_y = 3 if (r + 1) % 3 == 0 and r < 8 else 1
            cell.master.config(bg=t["line"])
            cell.master.grid_configure(padx=(0, bw_x), pady=(0, bw_y))
            cell.config(bg=t["grid"], fg=t["fixed"] if is_orig else t["user"], 
                        insertbackground=t["user"], font=(t["font"], 16, "bold"), 
                        readonlybackground=t["grid"])
        
        for btn in self.action_buttons:
            btn.master.config(bg=t["line"])
            btn.config(bg=t["bg"], fg=t["btn"], font=(t["font"], 8, "bold"), 
                       activebackground=t["btn"], activeforeground=t["bg"])

    def load_or_generate_data(self):
        today = str(date.today())
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if data.get("date") == today:
                        self.board = data.get("current_state")
                        self.original_puzzle = data.get("original")
                        return
            except: pass
        new_p = self.generate_puzzle()
        self.board = [row[:] for row in new_p]
        self.original_puzzle = [row[:] for row in new_p]

    def generate_puzzle(self, use_daily_seed=True):
        seed = int(date.today().strftime("%Y%m%d")) if use_daily_seed else random.randint(1, 1000000)
        random.seed(seed)
        base, side = 3, 9
        def pattern(r, c): return (base * (r % base) + r // base + c) % side
        def shuffle(s): return random.sample(s, len(s))
        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, side + 1))
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        for p in random.sample(range(side*side), int(side*side * 0.6)):
            board[p // side][p % side] = 0
        return board

    def save_cache(self):
        current_state = []
        for r in range(9):
            row = []
            for c in range(9):
                val = self.cells[(r, c)].get()
                row.append(int(val) if val else 0)
            current_state.append(row)
        
        data = {"date": str(date.today()), "original": self.original_puzzle, "current_state": current_state}
        with open(self.cache_file, 'w') as f:
            json.dump(data, f)
        self.set_status("Progress Saved!")
        self.root.after(2000, lambda: self.set_status("Ready"))

    def create_header(self):
        self.header = tk.Frame(self.root)
        self.header.pack(fill='x', padx=20, pady=(15, 5))
        self.header_label = tk.Label(self.header, text="SUDOKU")
        self.header_label.pack(side='left')
        self.close_btn = tk.Label(self.header, text=" [X] ", cursor="hand2")
        self.close_btn.pack(side='right')
        self.close_btn.bind("<Button-1>", lambda e: self.root.destroy())
        self.theme_btn = tk.Label(self.header, text=" THEME ", cursor="hand2")
        self.theme_btn.pack(side='right', padx=10)
        self.theme_btn.bind("<Button-1>", lambda e: self.cycle_theme())

    def cycle_theme(self):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.theme_names)
        self.apply_theme(self.theme_names[self.current_theme_idx])

    def create_grid(self):
        self.outer_grid = tk.Frame(self.root, padx=1, pady=1)
        self.outer_grid.pack(padx=20, pady=5)
        inner_grid = tk.Frame(self.outer_grid)
        inner_grid.pack()
        for r in range(9):
            for c in range(9):
                is_orig = self.original_puzzle[r][c] != 0
                val = self.board[r][c]
                cell_container = tk.Frame(inner_grid)
                cell_container.grid(row=r, column=c)
                cell = tk.Entry(cell_container, width=2, justify='center', bd=0, validate='key', validatecommand=self.vcmd)
                cell.pack(padx=1, pady=1, ipady=3)
                
                if val != 0: 
                    cell.insert(0, str(val))
                if is_orig: 
                    cell.config(state='readonly')
                
                # Bind arrow keys for navigation
                cell.bind("<Up>", lambda e, row=r, col=c: self.move_focus(row-1, col))
                cell.bind("<Down>", lambda e, row=r, col=c: self.move_focus(row+1, col))
                cell.bind("<Left>", lambda e, row=r, col=c: self.move_focus(row, col-1))
                cell.bind("<Right>", lambda e, row=r, col=c: self.move_focus(row, col+1))
                
                self.cells[(r, c)] = cell

    def move_focus(self, r, c):
        """Moves keyboard focus to the cell at (r, c) if it exists."""
        if (r, c) in self.cells:
            self.cells[(r, c)].focus_set()

    def create_controls(self):
        self.btn_container = tk.Frame(self.root)
        self.btn_container.pack(fill='x', padx=20, pady=5)
        self.action_buttons = []
        def make_btn(parent, text, cmd, side='top', fill='x'):
            outer = tk.Frame(parent, padx=1, pady=1)
            outer.pack(side=side, expand=True, fill=fill, pady=2, padx=2)
            btn = tk.Button(outer, text=text, command=cmd, bd=0, pady=5, cursor="hand2")
            btn.pack(fill='both')
            self.action_buttons.append(btn)
            return btn
        
        row1 = tk.Frame(self.btn_container)
        row1.pack(fill='x')
        make_btn(row1, "SAVE", self.save_cache, side='left', fill='both')
        make_btn(row1, "RESET", self.reset_current_grid, side='left', fill='both')
        make_btn(row1, "SOLVE", self.handle_solve, side='left', fill='both')
        
        row2 = tk.Frame(self.btn_container)
        row2.pack(fill='x')
        make_btn(row2, "RANDOM GRID", self.refresh_new_puzzle)

    def reset_current_grid(self):
        """Clears user progress but keeps the same starting puzzle."""
        for r in range(9):
            for c in range(9):
                cell = self.cells[(r, c)]
                if self.original_puzzle[r][c] == 0:
                    cell.config(state='normal')
                    cell.delete(0, tk.END)
        self.set_status("Grid Reset")
        self.root.after(1500, lambda: self.set_status("Ready"))

    def create_status_bar(self):
        self.status_frame = tk.Frame(self.root, pady=10)
        self.status_frame.pack(fill='x', padx=20)
        self.status_label = tk.Label(self.status_frame, text="Ready", anchor="center")
        self.status_label.pack(fill='x')

    def start_move(self, event):
        self.x, self.y = event.x, event.y
    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def handle_solve(self):
        solution = [row[:] for row in self.original_puzzle]
        if self.solve_backtrack(solution):
            for r in range(9):
                for c in range(9):
                    if self.original_puzzle[r][c] == 0:
                        cell = self.cells[(r, c)]
                        cell.config(state='normal')
                        cell.delete(0, tk.END)
                        cell.insert(0, str(solution[r][c]))
            self.check_completion()

    def solve_backtrack(self, b):
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for n in range(1, 10):
                        if self.is_valid(b, r, c, n):
                            b[r][c] = n
                            if self.solve_backtrack(b): return True
                            b[r][c] = 0
                    return False
        return True

    def is_valid(self, b, r, c, n):
        for i in range(9):
            if b[r][i] == n or b[i][c] == n: return False
        sr, sc = (r//3)*3, (c//3)*3
        for i in range(sr, sr+3):
            for j in range(sc, sc+3):
                if b[i][j] == n: return False
        return True

    def refresh_new_puzzle(self):
        new_p = self.generate_puzzle(use_daily_seed=False)
        self.original_puzzle = [row[:] for row in new_p]
        self.board = [row[:] for row in new_p]
        self.set_status("New Grid Generated")
        for r in range(9):
            for c in range(9):
                cell = self.cells[(r, c)]
                cell.config(state='normal')
                cell.delete(0, tk.END)
                if self.board[r][c] != 0:
                    cell.insert(0, str(self.board[r][c]))
                    cell.config(state='readonly')
        self.apply_theme(self.theme_names[self.current_theme_idx])

if __name__ == "__main__":
    root = tk.Tk()
    app = ThemeableSudoku(root)
    root.mainloop()
import os
from datetime import date

class ThemeableSudoku:
    def __init__(self, root):
        self.root = root
        self.root.title("SUDOKU WIDGET")
        
        # --- THEME DEFINITIONS ---
        self.themes = {
            "Future Retro": {
                "bg": "#0d0221", "grid": "#120438", "line": "#ff00ff", 
                "fixed": "#00ffff", "user": "#ffcc00", "btn": "#ea00d9", "font": "Consolas"
            },
            "Wooden Blocks": {
                "bg": "#3e2723", "grid": "#5d4037", "line": "#211007", 
                "fixed": "#ffcc80", "user": "#ffffff", "btn": "#ffcc80", "font": "Georgia"
            },
            "Paper Ink": {
                "bg": "#f5f5dc", "grid": "#ffffff", "line": "#000000", 
                "fixed": "#000080", "user": "#d32f2f", "btn": "#555555", "font": "Courier"
            },
            "Classic Grid": {
                "bg": "#ffffff", "grid": "#ffffff", "line": "#000000", 
                "fixed": "#000000", "user": "#0000ff", "btn": "#444444", "font": "Arial"
            },
            "Midnight OLED": {
                "bg": "#000000", "grid": "#111111", "line": "#333333", 
                "fixed": "#ffffff", "user": "#00ff00", "btn": "#444444", "font": "Verdana"
            },
            "Forest Nature": {
                "bg": "#1b5e20", "grid": "#2e7d32", "line": "#003300", 
                "fixed": "#c8e6c9", "user": "#ffff00", "btn": "#ffffff", "font": "Segoe UI"
            },
            "Royal Gold": {
                "bg": "#1a237e", "grid": "#283593", "line": "#ffd700", 
                "fixed": "#ffd700", "user": "#ffffff", "btn": "#ffd700", "font": "Times New Roman"
            }
        }
        
        self.theme_names = list(self.themes.keys())
        self.current_theme_idx = 0
        
        # Window Setup
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        self.cache_file = "sudoku_cache.json"
        self.cells = {}
        self.board = []
        self.original_puzzle = []
        
        # Register validation for entries
        self.vcmd = (self.root.register(self.validate_input), '%P')
        
        self.load_or_generate_data()
        self.create_header()
        self.create_grid()
        self.create_controls()
        
        # Apply initial theme
        self.apply_theme(self.theme_names[0])
        
        # Screen Position
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"340x540+{screen_w - 380}+80")
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def validate_input(self, P):
        if P == "" or (P.isdigit() and len(P) == 1 and P != '0'):
            return True
        return False

    def apply_theme(self, theme_name):
        t = self.themes[theme_name]
        self.root.configure(bg=t["bg"], highlightbackground=t["line"], highlightthickness=2)
        
        # Update Header & Containers (Fixing the black box glitch)
        self.header.config(bg=t["bg"])
        self.header_label.config(bg=t["bg"], fg=t["line"], font=(t["font"], 16, "bold"))
        self.theme_btn.config(bg=t["bg"], fg=t["line"], font=(t["font"], 9, "underline"))
        self.close_btn.config(bg=t["bg"], fg=t["line"], font=(t["font"], 12, "bold"))
        
        self.btn_container.config(bg=t["bg"])
        self.row1.config(bg=t["bg"])
        
        # Update Grid
        self.outer_grid.config(bg=t["line"])
        for (r, c), cell in self.cells.items():
            is_orig = self.original_puzzle[r][c] != 0
            
            bw_x = 3 if (c + 1) % 3 == 0 and c < 8 else 1
            bw_y = 3 if (r + 1) % 3 == 0 and r < 8 else 1
            cell.master.config(bg=t["line"]) 
            cell.master.grid_configure(padx=(0, bw_x), pady=(0, bw_y))
            
            # Adjusted ipady to ensure numbers don't get cut off when fonts change
            cell.config(
                bg=t["grid"],
                fg=t["fixed"] if is_orig else t["user"],
                insertbackground=t["user"],
                font=(t["font"], 16, "bold"),
                readonlybackground=t["grid"]
            )
            
        # Update Action Buttons
        for btn in self.action_buttons:
            btn.master.config(bg=t["line"]) 
            btn.config(
                bg=t["bg"], 
                fg=t["btn"], 
                font=(t["font"], 8, "bold"), 
                activebackground=t["btn"],
                activeforeground=t["bg"]
            )

    def cycle_theme(self):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.theme_names)
        self.apply_theme(self.theme_names[self.current_theme_idx])

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def generate_puzzle(self, use_daily_seed=True):
        seed = int(date.today().strftime("%Y%m%d")) if use_daily_seed else random.randint(1, 10000000)
        random.seed(seed)
        base, side = 3, 9
        def pattern(r, c): return (base * (r % base) + r // base + c) % side
        def shuffle(s): return random.sample(s, len(s))
        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, side + 1))
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        for p in random.sample(range(side*side), int(side*side * 0.6)):
            board[p // side][p % side] = 0
        return board

    def load_or_generate_data(self):
        today = str(date.today())
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if data.get("date") == today:
                        self.board = data.get("current_state")
                        self.original_puzzle = data.get("original")
                        return
            except: pass
        new_p = self.generate_puzzle(use_daily_seed=True)
        self.board = [row[:] for row in new_p]
        self.original_puzzle = [row[:] for row in new_p]

    def create_header(self):
        self.header = tk.Frame(self.root)
        self.header.pack(fill='x', padx=20, pady=(15, 5))
        
        self.header_label = tk.Label(self.header, text="SUDOKU")
        self.header_label.pack(side='left')
        
        self.close_btn = tk.Label(self.header, text=" [X] ", cursor="hand2")
        self.close_btn.pack(side='right')
        self.close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        self.theme_btn = tk.Label(self.header, text=" THEME ", cursor="hand2")
        self.theme_btn.pack(side='right', padx=10)
        self.theme_btn.bind("<Button-1>", lambda e: self.cycle_theme())

    def create_grid(self):
        self.outer_grid = tk.Frame(self.root, padx=1, pady=1)
        self.outer_grid.pack(padx=20, pady=5)
        
        inner_grid = tk.Frame(self.outer_grid)
        inner_grid.pack()

        for r in range(9):
            for c in range(9):
                is_orig = self.original_puzzle[r][c] != 0
                val = self.board[r][c]
                
                cell_container = tk.Frame(inner_grid)
                cell_container.grid(row=r, column=c)
                
                # width 2 and ipady 3 helps keep it compact and visible
                cell = tk.Entry(cell_container, width=2, justify='center', bd=0, 
                                validate='key', validatecommand=self.vcmd)
                cell.pack(padx=1, pady=1, ipady=3)
                
                if val != 0: 
                    cell.insert(0, str(val))
                if is_orig: 
                    cell.config(state='readonly')
                
                self.cells[(r, c)] = cell

    def create_controls(self):
        self.btn_container = tk.Frame(self.root)
        self.btn_container.pack(fill='x', padx=20, pady=5)
        self.action_buttons = []

        def make_btn(parent, text, cmd, side='top', fill='x'):
            outer = tk.Frame(parent, padx=1, pady=1)
            outer.pack(side=side, expand=True, fill=fill, pady=2, padx=2)
            btn = tk.Button(outer, text=text, command=cmd, bd=0, pady=5, cursor="hand2")
            btn.pack(fill='both')
            self.action_buttons.append(btn)
            return btn

        self.row1 = tk.Frame(self.btn_container)
        self.row1.pack(fill='x')
        
        make_btn(self.row1, "SAVE", self.save_cache, side='left', fill='both')
        make_btn(self.row1, "SOLVE", self.handle_solve, side='left', fill='both')
        make_btn(self.btn_container, "RANDOM GRID", self.refresh_new_puzzle)

    def save_cache(self):
        current_state = []
        for r in range(9):
            row = []
            for c in range(9):
                val = self.cells[(r, c)].get()
                row.append(int(val) if val.isdigit() else 0)
            current_state.append(row)
        data = {"date": str(date.today()), "original": self.original_puzzle, "current_state": current_state}
        with open(self.cache_file, 'w') as f:
            json.dump(data, f)

    def refresh_new_puzzle(self):
        new_p = self.generate_puzzle(use_daily_seed=False)
        self.original_puzzle = [row[:] for row in new_p]
        self.board = [row[:] for row in new_p]
        
        for r in range(9):
            for c in range(9):
                cell = self.cells[(r, c)]
                cell.config(state='normal')
                cell.delete(0, tk.END)
                val = self.board[r][c]
                if val != 0:
                    cell.insert(0, str(val))
                    cell.config(state='readonly')
        
        self.apply_theme(self.theme_names[self.current_theme_idx])
        self.save_cache()

    def handle_solve(self):
        solution = [row[:] for row in self.original_puzzle]
        if self.solve_backtrack(solution):
            for r in range(9):
                for c in range(9):
                    cell = self.cells[(r, c)]
                    if self.original_puzzle[r][c] == 0:
                        cell.config(state='normal')
                        cell.delete(0, tk.END)
                        cell.insert(0, str(solution[r][c]))
            self.save_cache()
        else:
            messagebox.showinfo("Sudoku", "No solution found.")

    def solve_backtrack(self, b):
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for n in range(1, 10):
                        if self.is_valid(b, r, c, n):
                            b[r][c] = n
                            if self.solve_backtrack(b): return True
                            b[r][c] = 0
                    return False
        return True

    def is_valid(self, b, r, c, n):
        for i in range(9):
            if b[r][i] == n or b[i][c] == n: return False
        sr, sc = (r//3)*3, (c//3)*3
        for i in range(sr, sr+3):
            for j in range(sc, sc+3):
                if b[i][j] == n: return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = ThemeableSudoku(root)
    root.mainloop()
