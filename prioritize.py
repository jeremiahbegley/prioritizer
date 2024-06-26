import numpy as np
import pandas as pd
import datetime
import sqlite3
import random

def open_connection():
    conn = sqlite3.connect('C:\sqlite\jb.db')
    cur = conn.cursor()
    return conn, cur

def get_item_info(cursor, schema, key_nm, item_key):
    query_string = f"SELECT * FROM {schema} WHERE {key_nm} = ?"
    data = cursor.execute(query_string,(item_key,))
    return data.fetchall()[0]

def get_k():
    return np.round((datetime.date.today() - datetime.date(1988, 8, 5)).days / 365.25,3)

def get_keys(cursor, schema):
    keys = []
    data = cursor.execute(f"SELECT * FROM {schema}").fetchall()
    for elem in data:
        keys.append(elem[0])
    return keys

def get_random_keys(item_keys):
    return random.sample(item_keys,2)

def get_expected_points(ra, rb):
    ea = (1/(1+10**((rb-ra)/400)))
    eb = (1/(1+10**((ra-rb)/400)))
    return ea, eb

def calculate_new_rating(r, e, s, k):
    return int(np.round(r + k*(s-e)))

def present_options(a,b):
    print(f'\n{a} or {b}?\n')
    print('Please:')
    print(f'PRESS 1 for {a}')
    print(f'PRESS 2 for {b}')
    print(f'PRESS 3 for a tie')
    print(f'PRESS 0 to return to the main menu')

def user_chooser(n):
    error_msg = 'Invalid input. Please try again.'
    while True:
        try:
            user_input = int(input())
            if user_input>=0 and user_input<=n:
                return user_input
            else:
                print(error_msg)
        except ValueError:
            print(error_msg)

def assign_results(user_input):
    if user_input==1:
        return 1.0,0.0
    elif user_input==2:
        return 0.0,1.0
    else:
        return 0.5,0.5

def generate_update_query(schema, key_nm, item_key, elo_rating, comparison_ct, last_change_dt):
    return f'''UPDATE {schema}
    SET elo_rating = {elo_rating},
    comparison_ct = {comparison_ct},
    last_change_dt = '{last_change_dt}'
    WHERE {key_nm} = '{item_key}';'''

def write_to_database(connection, cursor, queries):
    for q in queries:
        cursor.execute(q)
    connection.commit()
    return True

running = True
while running:
    print('Please:')
    print('PRESS 1 for task prioritization')
    print('PRESS 2 to manage your backlog of movies to see')
    print('PRESS 3 to rank movies you have already seen')
    print('PRESS 4 to to manage your backlog of books to read')
    print('PRESS 5 if you are Cordelia')
    print('PRESS 9 to rank 99.9 The Buzz songs')
    #print('PRESS 6 to test the program')
    print('PRESS 0 to exit the program')

    choice = user_chooser(9)

    if choice==1:
        session_schema = 'agenda'
    elif choice==2:
        session_schema = 'videnda'
    elif choice==3:
        session_schema = 'visa'
    elif choice==4:
        session_schema = 'legenda'
    elif choice==5:
        session_schema = 'visa_elo_cordelia'
    elif choice==6:
        session_schema = 'prioritizer_tester'
    elif choice==9:
        session_schema = 'buzz_elo'
    else:
        break

    while True:   
        conn, global_cursor = open_connection()
        session_k = get_k()
        session_date = datetime.date.today().strftime('%Y-%m-%d')
        session_keys = get_keys(global_cursor, session_schema)
        a_key,b_key = get_random_keys(session_keys)
        a,ra,ca = get_item_info(global_cursor,session_schema,'key',a_key)[1:4]
        b,rb,cb = get_item_info(global_cursor,session_schema,'key',b_key)[1:4]
        ea,eb = get_expected_points(ra,rb)
        present_options(a,b)
        user_input = user_chooser(4)
        if user_input==0:
            break
        else:
            sa,sb = assign_results(user_input)
        new_ra = calculate_new_rating(ra,ea,sa,session_k)
        new_rb = calculate_new_rating(rb,eb,sb,session_k)
        print(f'{a} is now at {new_ra}')
        print(f'{b} is now at {new_rb}')
        a_update = generate_update_query(session_schema, 'key', a_key, new_ra, ca+1, session_date)
        b_update = generate_update_query(session_schema, 'key', b_key, new_rb, cb+1, session_date)
        write_to_database(conn,global_cursor,[a_update,b_update])
        conn.close()