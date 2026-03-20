import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from datetime import date

class ModernSudokuWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Sudoku")
        
        # --- UI CONFIGURATION ---
        self.bg_main = "#121212"      
        self.bg_grid = "#1e1e1e"      
        self.color_fixed = "#00f0ff"  # Cyan
        self.color_user = "#ffcc00"   # Amber
        self.color_solve = "#ff3366"  # Pink
        self.accent = "#333333"       
        
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=self.bg_main, highlightthickness=1, highlightbackground="#333")
        
        self.cache_file = "sudoku_cache.json"
        self.cells = {}
        self.board = []
        self.original_puzzle = []
        
        self.load_or_generate_data()
        self.create_header()
        self.create_grid()
        self.create_controls()
        
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"320x500+{screen_w - 350}+100")
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
        # If daily, use date as seed. If not, use a random seed.
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
        
        # Difficulty: remove 65% of cells
        for p in random.sample(range(side*side), int(side*side * 0.65)):
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

    def refresh_new_puzzle(self):
        """Generates a completely new random puzzle."""
        new_p = self.generate_puzzle(use_daily_seed=False)
        self.original_puzzle = [row[:] for row in new_p]
        self.board = [row[:] for row in new_p]
        
        # Update UI Cells
        for r in range(9):
            for c in range(9):
                cell = self.cells[(r, c)]
                cell.config(state='normal')
                cell.delete(0, tk.END)
                val = self.board[r][c]
                if val != 0:
                    cell.insert(0, str(val))
                    cell.config(state='readonly', readonlybackground=self.bg_grid, fg=self.color_fixed)
                else:
                    cell.config(fg=self.color_user)
        
        # Save this as the "current" state for today
        self.save_cache()

    def create_header(self):
        header = tk.Frame(self.root, bg=self.bg_main)
        header.pack(fill='x', padx=15, pady=(15, 5))
        tk.Label(header, text="SUDOKU", bg=self.bg_main, fg="white", font=("Impact", 20)).pack(side='left')
        
        exit_btn = tk.Label(header, text="✕", bg=self.bg_main, fg="#555", font=("Arial", 12, "bold"), cursor="hand2")
        exit_btn.pack(side='right')
        exit_btn.bind("<Button-1>", lambda e: self.root.destroy())
        exit_btn.bind("<Enter>", lambda e: exit_btn.config(fg="white"))
        exit_btn.bind("<Leave>", lambda e: exit_btn.config(fg="#555"))

    def create_grid(self):
        grid_container = tk.Frame(self.root, bg=self.accent, padx=1, pady=1)
        grid_container.pack(pady=10, padx=15)

        for r in range(9):
            for c in range(9):
                is_orig = self.original_puzzle[r][c] != 0
                val = self.board[r][c]
                padx = (1, 1) if (c + 1) % 3 != 0 else (1, 3)
                pady = (1, 1) if (r + 1) % 3 != 0 else (1, 3)
                
                cell = tk.Entry(grid_container, width=2, font=('Consolas', 16, 'bold'), 
                                justify='center', bd=0, bg=self.bg_grid, 
                                fg=self.color_fixed if is_orig else self.color_user,
                                insertbackground="white")
                cell.grid(row=r, column=c, padx=padx, pady=pady, ipady=5)
                
                if val != 0: cell.insert(0, str(val))
                if is_orig: cell.config(state='readonly', readonlybackground=self.bg_grid)
                self.cells[(r, c)] = cell

    def create_controls(self):
        # Button frame 1 (Save and Solve)
        btn_frame1 = tk.Frame(self.root, bg=self.bg_main)
        btn_frame1.pack(fill='x', padx=15, pady=(5, 2))

        # Button frame 2 (Refresh)
        btn_frame2 = tk.Frame(self.root, bg=self.bg_main)
        btn_frame2.pack(fill='x', padx=15, pady=5)

        def create_btn(parent, text, cmd, color):
            btn = tk.Button(parent, text=text, command=cmd, bg=color, fg="white",
                            font=("Arial", 8, "bold"), bd=0, pady=8, cursor="hand2",
                            activebackground="#444", activeforeground="white")
            btn.pack(side='left', expand=True, fill='x', padx=2)
            return btn

        create_btn(btn_frame1, "SAVE PROGRESS", self.save_cache, "#333333")
        create_btn(btn_frame1, "SOLVE DAILY", self.handle_solve, "#007acc")
        create_btn(btn_frame2, "NEW RANDOM PUZZLE", self.refresh_new_puzzle, "#444444")

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

    def handle_solve(self):
        solution = [row[:] for row in self.original_puzzle]
        if self.solve_backtrack(solution):
            for r in range(9):
                for c in range(9):
                    if self.original_puzzle[r][c] == 0:
                        self.cells[(r, c)].config(state='normal')
                        self.cells[(r, c)].delete(0, tk.END)
                        self.cells[(r, c)].insert(0, str(solution[r][c]))
                        self.cells[(r, c)].config(fg=self.color_solve)
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
    app = ModernSudokuWidget(root)
    root.mainloop()