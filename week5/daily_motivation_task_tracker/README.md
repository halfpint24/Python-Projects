# Daily Motivation Task Tracker ✅

A simple Python3 script that helps you set **three daily goals**, mark them as done, and keep a **completion streak**—with a quick dose of motivation (quote + fun fact) each run.

---

## Requirements
- Python **3.7+**
- No external dependencies
- Write access to the current directory (creates/updates `goals.csv` and `streaks.csv`)

---

## Usage

Run the script using:

```bash
python3 daily_motivation_task_tracker.py [OPTIONS]
```

### Options

- **`--summary`**  
  Show a concise **summary** for the current user (today’s goals + last 7 days + current streak).  
  ```bash
  python3 daily_motivation_task_tracker.py --summary
  ```

- **`--user <username>`**  
  Provide a **username** non-interactively (otherwise you’ll be prompted).  
  ```bash
  python3 daily_motivation_task_tracker.py --user alice
  ```

If no arguments are passed, the script will:
1. Show a motivational **quote** and **fun fact**.  
2. Prompt you to enter or update your 3 daily goals.  
3. Ask if you’ve completed each goal.  
4. Save your progress and update your streak.

---

## Examples

```bash
# Run interactively (default)
python3 daily_motivation_task_tracker.py

# Show today’s summary
python3 daily_motivation_task_tracker.py --summary

# Run with a username (non-interactive prompt)
python3 daily_motivation_task_tracker.py --user bob
```

---

## Files Created

- **`goals.csv`**  
  Stores daily goals and completion status.

- **`streaks.csv`**  
  Tracks daily streak progress.

---

## Features
- Input or update **3 daily goals**.  
- Mark goals as **done/not done**.  
- Tracks a **completion streak** (number of consecutive days all goals done).  
- Shows motivational **quotes** and **fun facts**.  
- Provides a **7-day history** and summary view.  
