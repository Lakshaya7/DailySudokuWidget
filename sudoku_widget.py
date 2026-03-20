import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from datetime import date

class FutureRetroSudoku:
    def __init__(self, root):
        self.root = root
        self.root.title("NEON SUDOKU")
        
        # --- SYNTHWAVE PALETTE ---
        self.bg_dark = "#0d0221"      # Deep Space Purple
        self.bg_cell = "#120438"      # Cyber Cell Background
        self.neon_pink = "#ff00ff"    # Major Grid Glow
        self.neon_cyan = "#00ffff"    # Fixed Numbers
        self.neon_amber = "#ffcc00"   # User Input
        self.neon_magenta = "#ea00d9" # Solved State
        self.grid_dim = "#3d0b5e"     # Minor Grid Lines
        
        # Window Setup
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=self.bg_dark, highlightthickness=2, highlightbackground=self.neon_pink)
        
        self.cache_file = "sudoku_cache.json"
        self.cells = {}
        self.board = []
        self.original_puzzle = []
        
        self.load_or_generate_data()
        self.create_header()
        self.create_grid()
        self.create_controls()
        
        # Screen Position & Dragging
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"340x540+{screen_w - 380}+80")
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

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
        header = tk.Frame(self.root, bg=self.bg_dark)
        header.pack(fill='x', padx=20, pady=(20, 10))
        
        # Futuristic Title
        tk.Label(header, text="SYSTEM://SUDOKU", bg=self.bg_dark, fg=self.neon_pink, 
                 font=("Consolas", 16, "bold")).pack(side='left')
        
        # Cyber Close Button
        close_btn = tk.Label(header, text="[X]", bg=self.bg_dark, fg=self.grid_dim, 
                             font=("Consolas", 12, "bold"), cursor="hand2")
        close_btn.pack(side='right')
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=self.neon_pink))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=self.grid_dim))

    def create_grid(self):
        # The main grid container with a "glow" border
        outer_grid = tk.Frame(self.root, bg=self.neon_pink, padx=1, pady=1)
        outer_grid.pack(padx=20, pady=10)
        
        inner_grid = tk.Frame(outer_grid, bg=self.bg_dark)
        inner_grid.pack()

        for r in range(9):
            for c in range(9):
                is_orig = self.original_puzzle[r][c] != 0
                val = self.board[r][c]
                
                # Visual grouping for 3x3 blocks with neon highlights
                bw_x = 3 if (c + 1) % 3 == 0 and c < 8 else 1
                bw_y = 3 if (r + 1) % 3 == 0 and r < 8 else 1
                
                cell_container = tk.Frame(inner_grid, bg=self.neon_pink if (bw_x == 3 or bw_y == 3) else self.grid_dim)
                cell_container.grid(row=r, column=c, padx=(0, bw_x), pady=(0, bw_y))
                
                cell = tk.Entry(cell_container, width=2, font=('Consolas', 18, 'bold'), 
                                justify='center', bd=0, bg=self.bg_cell, 
                                fg=self.neon_cyan if is_orig else self.neon_amber,
                                insertbackground=self.neon_amber)
                cell.pack(padx=1, pady=1, ipady=4)
                
                if val != 0: cell.insert(0, str(val))
                if is_orig: cell.config(state='readonly', readonlybackground=self.bg_cell)
                
                self.cells[(r, c)] = cell

    def create_controls(self):
        btn_container = tk.Frame(self.root, bg=self.bg_dark)
        btn_container.pack(fill='x', padx=20, pady=10)

        def make_cyber_btn(text, cmd, color, side='top', fill='x'):
            # Double frame for neon outline effect
            outer = tk.Frame(btn_container, bg=color, padx=1, pady=1)
            outer.pack(side=side, expand=True, fill=fill, pady=4, padx=2)
            
            btn = tk.Button(outer, text=text, command=cmd, bg=self.bg_dark, fg=color,
                            font=("Consolas", 9, "bold"), bd=0, pady=6, cursor="hand2",
                            activebackground=color, activeforeground=self.bg_dark)
            btn.pack(fill='both')
            
            # Hover effects
            btn.bind("<Enter>", lambda e: outer.config(bg="white"))
            btn.bind("<Leave>", lambda e: outer.config(bg=color))
            return btn

        row1 = tk.Frame(btn_container, bg=self.bg_dark)
        row1.pack(fill='x')
        
        make_cyber_btn("SAVE_STATE", self.save_cache, self.neon_cyan, side='left', fill='both')
        make_cyber_btn("EXEC_SOLVE", self.handle_solve, self.neon_magenta, side='left', fill='both')
        make_cyber_btn("GENERATE_NEW_GRID", self.refresh_new_puzzle, self.neon_pink)

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
                    cell.config(state='readonly', readonlybackground=self.bg_cell, fg=self.neon_cyan)
                else:
                    cell.config(fg=self.neon_amber)
        self.save_cache()

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
                        cell.config(fg=self.neon_magenta)
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
    app = FutureRetroSudoku(root)
    root.mainloop()