import json
import csv
import random
import argparse
import os
import pandas as pd
from datetime import datetime


def load_jokes_and_facts():
    global jokes, facts
    with open('jokes.json', 'r', encoding='utf-8') as f:
        jokes = json.load(f)
    with open('facts.json', 'r', encoding='utf-8') as f:
        facts = json.load(f)

        
def pick_and_print_randoms():
    global random_joke, random_fact
    random_joke = random.choice(jokes)
    random_fact = random.choice(facts)
    print(random_joke)
    print('Fun fact: {}'.format(random_fact))

    
def get_joke_rating():
    joke_rating = None
    while True:
        try:
            joke_rating = int(input('Rate this joke (1-5): '))
            if joke_rating >= 1 and joke_rating <= 5:
                break
            else:
                print('Invalid input, try again')
        except ValueError:
            print('Input not a number, try again')
    return joke_rating


def set_timestamp():
    global timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    
def get_last_id(filename):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return 0  # file doesn’t exist or is empty

    with open(filename, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

        if len(rows) <= 1:  # only header or nothing
            return 0
        
        # Last row, first column = ID
        return int(rows[-1][0])

    
def write_rating_row():
    with open('rating_data.csv', 'a+', newline='') as f:
        f.seek(0)  # move to beginning to check if empty
        is_empty = f.read(1) == ''
        f.seek(0, 2)  # move back to end for writing
        
        writer = csv.writer(f)

        last_id = get_last_id('rating_data.csv')

        # Write header if file is empty
        if is_empty:
            writer.writerow(['ID', 'Timestamp', 'Rating', 'Joke', 'Fact'])
        
        # Write the new row
        writer.writerow([last_id + 1, timestamp, joke_rating, random_joke, random_fact])

        
def load_rating_df():
    global rating_df
    rating_df = pd.read_csv('rating_data.csv')

    
def print_best_jokes_today(df):
    best_jokes_today = df.sort_values(
    by=['Timestamp', 'Rating'],
    ascending=[False, False]
    ).head(5)
    print('-----------------------')
    print('BEST JOKES TODAY')
    print('-----------------------')
    print(best_jokes_today[['Timestamp', 'Rating', 'Joke']])


def print_best_joke_all_time(df):
    best_joke_all_time = rating_df.sort_values(by='Rating', ascending=False).head(1)
    print('-----------------------')
    print('BEST JOKE ALL TIME')
    print('-----------------------')
    print(best_joke_all_time[['Timestamp', 'Rating', 'Joke']])

    
def add_joke(joke):
    jokes.append(joke)
    with open('jokes.json', 'w') as f:
        json.dump(jokes, f)

        
def add_fact(fact):
    facts.append(fact)
    with open('facts.json', 'w') as f:
        json.dump(facts, f)

        
def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--serve', dest='serve', action='store_true')
        parser.add_argument('--noserve', dest='serve', action='store_false')
        parser.set_defaults(serve=True)
        parser.add_argument('--top', choices=['today', 'all', 'both'], default='')
        parser.add_argument('--add', nargs=2, default='')
        args = parser.parse_args()

        if args.serve:
            global joke_rating
            load_jokes_and_facts()
            pick_and_print_randoms()
            joke_rating = get_joke_rating()
            set_timestamp()
            write_rating_row()

        load_rating_df()
        if args.top == 'today':
            print_best_jokes_today(rating_df)
        if args.top == 'all':
            print_best_joke_all_time(rating_df)
        if args.top == 'both':
            print_best_jokes_today(rating_df)
            print_best_joke_all_time(rating_df)

        if args.add != '':
            if args.add[0].lower() == 'joke':
                add_joke(args.add[1])
            if args.add[0].lower() == 'fact':
                add_fact(args.add[1])
    except FileNotFoundError:
        print('Error: rating data not found')


if __name__ == '__main__':
    main()
