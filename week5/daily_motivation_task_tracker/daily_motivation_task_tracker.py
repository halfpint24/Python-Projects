import argparse
import csv
import os
import random
from datetime import datetime, timedelta

TODAY = datetime.now().strftime("%Y-%m-%d")
GOALS_FILE = "goals.csv"
STREAKS_FILE = "streaks.csv"

QUOTES = [
    "Small steps every day lead to big results.",
    "Done is better than perfect.",
    "You don’t have to be extreme, just consistent.",
    "Start where you are. Use what you have. Do what you can.",
    "Discipline is choosing what you want most over what you want now.",
]
FUN_FACTS = [
    "Bananas are berries, but strawberries aren’t.",
    "Honey never spoils.",
    "Octopuses have three hearts.",
    "Your brain uses ~20% of your energy.",
    "A day on Venus is longer than a year on Venus.",
]

GOAL_FIELDS = ["date","username","goal_1","goal_2","goal_3","done_1","done_2","done_3"]
STREAK_FIELDS = ["date","username","completed_all","current_streak"]

def ensure_file(path, header):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=header).writeheader()

def read_rows(path):
    ensure_file(path, GOAL_FIELDS if path==GOALS_FILE else STREAK_FIELDS)
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def write_rows(path, rows, header):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def get_username(arg_user):
    if arg_user: return arg_user
    while True:
        name = input("Enter your username: ").strip()
        if name: return name

def show_motivation():
    print("-"*48)
    print(random.choice(QUOTES))
    print("Fun fact:", random.choice(FUN_FACTS))
    print("-"*48)

def yesno(prompt, default="n"):
    s = input(f"{prompt} (y/n) [{default}]: ").strip().lower()
    return (s or default).startswith("y")

def get_today_row(goals, user):
    for r in goals:
        if r["date"] == TODAY and r["username"].lower() == user.lower():
            return r
    return None

def prompt_goals():
    g1 = input("Goal 1: ").strip()
    g2 = input("Goal 2: ").strip()
    g3 = input("Goal 3: ").strip()
    return g1, g2, g3

def prompt_done(existing=None):
    def ask(i, default):
        s = input(f"Is goal {i} done? (y/n) [{default}]: ").strip().lower()
        s = s or default
        return "1" if s.startswith("y") else "0"
    d1 = "y" if existing and existing.get("done_1") == "1" else "n"
    d2 = "y" if existing and existing.get("done_2") == "1" else "n"
    d3 = "y" if existing and existing.get("done_3") == "1" else "n"
    return ask(1,d1), ask(2,d2), ask(3,d3)

def save_today(goals, user, g1,g2,g3,d1,d2,d3):
    row = get_today_row(goals, user)
    if row:
        row.update({"goal_1":g1,"goal_2":g2,"goal_3":g3,"done_1":d1,"done_2":d2,"done_3":d3})
    else:
        goals.append({"date":TODAY,"username":user,"goal_1":g1,"goal_2":g2,"goal_3":g3,"done_1":d1,"done_2":d2,"done_3":d3})
    write_rows(GOALS_FILE, goals, GOAL_FIELDS)

def completed_all(goals, date_str, user):
    for r in goals:
        if r["date"]==date_str and r["username"].lower()==user.lower():
            return r["done_1"]=="1" and r["done_2"]=="1" and r["done_3"]=="1"
    return False

def update_streaks(goals, user):
    # Build a set of dates where all goals were completed for this user
    done_days = set(r["date"] for r in goals
                    if r["username"].lower()==user.lower()
                    and r["done_1"]=="1" and r["done_2"]=="1" and r["done_3"]=="1")
    # Count back from today
    streak = 0
    cur = datetime.strptime(TODAY, "%Y-%m-%d")
    while cur.strftime("%Y-%m-%d") in done_days:
        streak += 1
        cur -= timedelta(days=1)
    comp_today = TODAY in done_days

    streaks = read_rows(STREAKS_FILE)

    found = False
    for r in streaks:
        if r["date"]==TODAY and r["username"].lower()==user.lower():
            r.update({"completed_all":"1" if comp_today else "0", "current_streak":str(streak)})
            found = True
            break
    if not found:
        streaks.append({"date":TODAY,"username":user,"completed_all":"1" if comp_today else "0","current_streak":str(streak)})
    write_rows(STREAKS_FILE, streaks, STREAK_FIELDS)
    return streak, comp_today

def show_summary(user):
    goals = read_rows(GOALS_FILE)
    print("-"*48)
    print(f"SUMMARY for {user}")
    print("-"*48)
    r = get_today_row(goals, user)
    if r:
        print(f"Today ({TODAY})")
        print(f"  1) {r['goal_1']} [{'✔' if r['done_1']=='1' else ' '}]")
        print(f"  2) {r['goal_2']} [{'✔' if r['done_2']=='1' else ' '}]")
        print(f"  3) {r['goal_3']} [{'✔' if r['done_3']=='1' else ' '}]")
    else:
        print(f"Today ({TODAY}): no goals recorded.")

    print("\nLast 7 days:")
    start = (datetime.strptime(TODAY,"%Y-%m-%d") - timedelta(days=6)).strftime("%Y-%m-%d")
    dates = [(datetime.strptime(start,"%Y-%m-%d")+timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    any_data = False
    for d in dates:
        if completed_all(goals, d, user):
            print(f"  {d}: [✔] all done")
            any_data = True
        else:
            # only print line if there is a record that day or it's today
            has_row = any((g["date"]==d and g["username"].lower()==user.lower()) for g in goals)
            if has_row:
                print(f"  {d}: [ ] not all done")
                any_data = True
    if not any_data:
        print("  No entries in the last 7 days.")

    # Show current streak (compute quickly)
    streak, _ = update_streaks(goals, user)
    print(f"\nCurrent streak: {streak} day(s)")
    print("-"*48)

def end_of_day_message(user, all_done, streak):
    if all_done:
        print(f"Great job, {user}! You finished all your goals today.")
        print(f"Streak: {streak} day(s). Keep it going!")
    else:
        print(f"Nice work today, {user}. Progress beats perfection.")
        if streak > 0:
            print(f"Current streak: {streak} day(s) — add to it tomorrow!")
        else:
            print("Let’s start a streak tomorrow. You’ve got this!")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    user = get_username(args.user)

    if args.summary:
        show_summary(user)
        return

    show_motivation()
    goals = read_rows(GOALS_FILE)

    r = get_today_row(goals, user)
    if r:
        print("Goals found for today. Update them below.")
        print(f" 1) {r['goal_1']}\n 2) {r['goal_2']}\n 3) {r['goal_3']}")
        if yesno("Edit goal text?", "n"):
            r["goal_1"] = input("Update Goal 1 (blank = keep): ").strip() or r["goal_1"]
            r["goal_2"] = input("Update Goal 2 (blank = keep): ").strip() or r["goal_2"]
            r["goal_3"] = input("Update Goal 3 (blank = keep): ").strip() or r["goal_3"]
        d1,d2,d3 = prompt_done(r)
        save_today(goals, user, r["goal_1"], r["goal_2"], r["goal_3"], d1,d2,d3)
    else:
        print("Enter your 3 goals for today:")
        g1,g2,g3 = prompt_goals()
        save_today(goals, user, g1,g2,g3, "0","0","0")

    # Update streaks and show summary/message
    goals = read_rows(GOALS_FILE)  # reload
    streak, all_done = update_streaks(goals, user)
    show_summary(user)
    end_of_day_message(user, all_done, streak)

if __name__ == "__main__":
    main()
