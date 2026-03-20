import tkinter as tk
from tkinter import messagebox
import random
import json
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
                "fixed": "#ffcc80", "user": "#ffffff", "btn": "#8d6e63", "font": "Georgia"
            },
            "Paper Ink": {
                "bg": "#f5f5dc", "grid": "#ffffff", "line": "#000000", 
                "fixed": "#000080", "user": "#d32f2f", "btn": "#9e9e9e", "font": "Courier"
            },
            "Classic Grid": {
                "bg": "#ffffff", "grid": "#ffffff", "line": "#000000", 
                "fixed": "#000000", "user": "#0000ff", "btn": "#e0e0e0", "font": "Arial"
            },
            "Midnight OLED": {
                "bg": "#000000", "grid": "#111111", "line": "#333333", 
                "fixed": "#ffffff", "user": "#00ff00", "btn": "#222222", "font": "Verdana"
            },
            "Forest Nature": {
                "bg": "#1b5e20", "grid": "#2e7d32", "line": "#003300", 
                "fixed": "#c8e6c9", "user": "#ffff00", "btn": "#4caf50", "font": "Segoe UI"
            },
            "Royal Gold": {
                "bg": "#1a237e", "grid": "#283593", "line": "#ffd700", 
                "fixed": "#ffd700", "user": "#ffffff", "btn": "#3949ab", "font": "Times New Roman"
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
        
        self.load_or_generate_data()
        self.create_header()
        self.create_grid()
        self.create_controls()
        
        # Apply initial theme
        self.apply_theme(self.theme_names[0])
        
        # Screen Position
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"340x560+{screen_w - 380}+80")
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def apply_theme(self, theme_name):
        t = self.themes[theme_name]
        self.root.configure(bg=t["bg"], highlightbackground=t["line"], highlightthickness=2)
        
        # Update Header
        self.header_label.config(bg=t["bg"], fg=t["line"], font=(t["font"], 14, "bold"))
        self.theme_btn.config(bg=t["bg"], fg=t["line"], font=(t["font"], 8))
        self.close_btn.config(bg=t["bg"], fg=t["line"])
        
        # Update Grid
        self.outer_grid.config(bg=t["line"])
        for (r, c), cell in self.cells.items():
            is_orig = self.original_puzzle[r][c] != 0
            
            # Thick lines logic
            bw_x = 3 if (c + 1) % 3 == 0 and c < 8 else 1
            bw_y = 3 if (r + 1) % 3 == 0 and r < 8 else 1
            cell.master.config(bg=t["line"]) # Container frame
            cell.master.grid_configure(padx=(0, bw_x), pady=(0, bw_y))
            
            cell.config(
                bg=t["grid"],
                fg=t["fixed"] if is_orig else t["user"],
                insertbackground=t["user"],
                font=(t["font"], 18, "bold"),
                readonlybackground=t["grid"]
            )
            
        # Update Buttons
        for btn in self.action_buttons:
            btn.master.config(bg=t["line"]) # Outline frame
            btn.config(bg=t["bg"], fg=t["btn"], font=(t["font"], 8, "bold"), activebackground=t["btn"])

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
        seed = int(date.today().strftime("%Y%m%d")) if use_daily_seed else random.randint(1, 1e7)
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
        header = tk.Frame(self.root)
        header.pack(fill='x', padx=20, pady=(15, 5))
        
        self.header_label = tk.Label(header, text="SUDOKU")
        self.header_label.pack(side='left')
        
        self.close_btn = tk.Label(header, text=" [X] ", cursor="hand2")
        self.close_btn.pack(side='right')
        self.close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        self.theme_btn = tk.Label(header, text=" CHANGE THEME ", cursor="hand2", pady=5)
        self.theme_btn.pack(side='right', padx=10)
        self.theme_btn.bind("<Button-1>", lambda e: self.cycle_theme())

    def create_grid(self):
        self.outer_grid = tk.Frame(self.root, padx=1, pady=1)
        self.outer_grid.pack(padx=20, pady=10)
        
        inner_grid = tk.Frame(self.outer_grid)
        inner_grid.pack()

        for r in range(9):
            for c in range(9):
                is_orig = self.original_puzzle[r][c] != 0
                val = self.board[r][c]
                
                cell_container = tk.Frame(inner_grid)
                cell_container.grid(row=r, column=c)
                
                cell = tk.Entry(cell_container, width=2, justify='center', bd=0)
                cell.pack(padx=1, pady=1, ipady=4)
                
                if val != 0: cell.insert(0, str(val))
                if is_orig: cell.config(state='readonly')
                
                self.cells[(r, c)] = cell

    def create_controls(self):
        self.btn_container = tk.Frame(self.root)
        self.btn_container.pack(fill='x', padx=20, pady=10)
        self.action_buttons = []

        def make_btn(text, cmd, side='top', fill='x'):
            outer = tk.Frame(self.btn_container, padx=1, pady=1)
            outer.pack(side=side, expand=True, fill=fill, pady=2, padx=2)
            btn = tk.Button(outer, text=text, command=cmd, bd=0, pady=5, cursor="hand2")
            btn.pack(fill='both')
            self.action_buttons.append(btn)
            return btn

        row1 = tk.Frame(self.btn_container)
        row1.pack(fill='x')
        
        make_btn("SAVE PROGRESS", self.save_cache, side='left', fill='both')
        make_btn("SOLVE DAILY", self.handle_solve, side='left', fill='both')
        make_btn("NEW RANDOM GRID", self.refresh_new_puzzle)

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
        self.current_theme_idx -= 1 # Keep same theme
        self.cycle_theme()

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
            self.save_cache()

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