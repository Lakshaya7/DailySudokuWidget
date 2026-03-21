🧩 Daily Sudoku Desktop Widget

A sleek, lightweight, and themeable Sudoku widget for your desktop. Built with Python and Tkinter, this application features a daily-synchronized puzzle engine, a recursive backtracking solver, and persistent local caching.

🚀 Key Features

📅 Daily Challenge Generates a unique puzzle every 24 hours based on the system date. Every user globally receives the same challenge for the day.

🎨 7 Premium Themes Dynamic UI switching with a single click:

Future Retro: Neon Synthwave aesthetic.

Wooden Blocks: Warm timber tones with serif fonts.

Midnight OLED: Pure black background for high-contrast setups.

Paper Ink: Classic newspaper style.

Forest, Classic, and Royal Gold.

💾 Persistent Cache Automatically saves progress to sudoku_cache.json. Resume your game exactly where you left off.

🤖 Integrated Solver A built-in engine that solves any valid state using a recursive backtracking algorithm.

🎲 Random Mode Beyond the daily challenge, generate infinite unique puzzles instantly for endless practice.

🪟 True Widget Experience Borderless, "Always-on-top" window that is fully draggable across your workspace.

🛠️ Technical Architecture

1. The Daily Seed Engine

The application utilizes a Seeded Randomization strategy. By passing the current date as a seed to the random number generator, the algorithm produces the same board layout for the duration of the day.

    # Technical snippet of the seeding logic
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)


2. Backtracking Solver

The solver implements a classic Recursive Backtracking Algorithm:

Search: Find the next empty cell ($0$).

Iterate: Attempt to place digits $1$ through $9$.

Validate: Check the digit against Sudoku constraints (Row, Column, and $3 \times 3$ Subgrid).

Recurse: If valid, proceed to the next cell.

Backtrack: If a dead-end is reached, undo the choice and try the next candidate.

📦 Installation & Setup

Prerequisites

 - Python 3.x

 - Git (for version control)

Quick Start

Clone the repository:

    git clone [https://github.com/YOUR_USERNAME/DailySudoku.git](https://github.com/YOUR_USERNAME/DailySudoku.git)
    cd DailySudoku


Run the script:

    python sudoku_widget.py


Desktop Widget Mode (Windows)

To run the app as a silent background process without a terminal window:

Double-click run_Sudoku.bat

Auto-start: To launch on system boot, copy run_Sudoku.bat into your Windows Startup folder (shell:startup).

🕹️ Controls

Drag: Click and hold the header or background to move the widget.

Input: Type numbers $1-9$ directly into the grid.

Theme: Click the THEME link in the header to cycle through styles.

[X]: Closes the application process completely.

Developed as a learning project for Python UI development and Algorithm implementation.
