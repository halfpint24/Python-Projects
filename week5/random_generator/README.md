# Random Generator 🎲

A simple Python3 script that generates random jokes and facts, keeps track of a leaderboard, and lets you add new content interactively.

---

## Requirements
- Python 3.7+
- No external dependencies (unless you’ve added some to `random_generator.py`)

---

## Usage

Run the script using:

```bash
python3 random_generator.py [OPTIONS]
```

### Options

- **`--serve`** *(default)*  
  Shows a random **joke** and **fact**, also prompts the user for a rating.  
  ```bash
  python3 random_generator.py --serve
  ```
  If no argument is passed, this is the default behavior.
  
- **`--noserve`**  
  Do not display a random joke and fact. Does not prompt the user for a rating.  
  ```bash
  python3 random_generator.py --noserve
  ```

- **`--top today`**  
  Displays today’s **leaderboard** (most popular jokes for the day).  
  ```bash
  python3 random_generator.py --top today
  ```

- **`--top all`**  
  Displays the **all-time best** joke.  
  ```bash
  python3 random_generator.py --top all
  ```
  
  - **`--top both`**  
  Displays the two top options listed above.  
  ```bash
  python3 random_generator.py --top both
  ```

- **`--add`**  
  Launches interactive mode to add new jokes or facts to the collection.  
  ```bash
  python3 random_generator.py --add [joke|fact] 'put joke/fact here'
  ```

## Examples

```bash
# Show a joke and fact and prompt the user for a rating (default)
python3 random_generator.py

# Show today’s leaderboard
python3 random_generator.py --noserve --top today

# Show all-time best joke
python3 random_generator.py --noserve --top all

# Add new jokes/facts interactively
python3 random_generator.py --noserve --add joke 'a bad joke'
python3 random_generator.py --noserve --add fact 'a random fact'
```

