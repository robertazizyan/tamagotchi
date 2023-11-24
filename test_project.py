import project
import pytest
import sqlite3
import csv
import re
from unittest.mock import patch
from werkzeug.security import generate_password_hash, check_password_hash


'''
The 3 functions below serve as a template for connection to the test database to be used in testing the User and Tamagotchi class
'''

# Return conn and cursor objects for sqlite3 operations
def connect():
    try:
        conn = sqlite3.connect('database_test.db')
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(e)
        exit()

# Insert necessary data into the users and/or tamagotchi tables from the database_test.db and commit those changes
def alter_database(conn, cursor, username = None, password = None, names = None):
    if username and password:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, generate_password_hash(password)))
        
    if username and names:
        for item in names:
            cursor.execute('INSERT INTO tamagotchi (user_id, name) VALUES ((SELECT id FROM users WHERE username = ?), ?)', (username, item))
    
    conn.commit()

# Revert database_test.db to its original state with NO DATA whatsoever, commit the changes and close the connection
def revert_database(conn, cursor):
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM tamagotchi')
        
    conn.commit()
    conn.close()
    
'''
The function below is to be used ONLY AT THE END OF THE LAST TEST
since it deletes all the save data for the usernames that have 'test (and maybe digits after)' in them
'''
def revert_savefile():
    with open('saves.csv', mode = 'r') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader if not re.search(r'^test\d{0,2}', row['username'])]
    
    with open('saves.csv', mode = 'w') as file:
        writer = csv.DictWriter(file, fieldnames = reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

'''
5 Functions below test the menus of the game without passing in the user object
'''    
def test_show_main_menu():
    with pytest.raises(TypeError):
        project.show_main_menu()


def test_show_food_menu():
    with pytest.raises(TypeError):
        project.show_food_menu()


def test_show_interaction_menu():
    with pytest.raises(TypeError):
        project.show_interaction_menu()


def test_show_status_menu():
    with pytest.raises(TypeError):
        project.show_status_menu()


def test_game_exit():
    with pytest.raises(TypeError):
        project.game_exit()


# Assert the work of the status capping function 
def test_min_max():
    assert project.min_max(0) == 0
    assert project.min_max(100) == 100
    assert project.min_max(-1) == 0
    assert project.min_max(101) == 100
    assert project.min_max(50) == 50


# Well i mean this is a test right?
def test_clear_terminal():
    assert project.clear_terminal() == None


# And this too...
def test_animated_print():
    assert project.animated_print('hello') == None
    
    with pytest.raises(TypeError):
        project.animated_print(123)
        
    with pytest.raises(TypeError):
        project.animated_print()


'''
Moving on to User class tests. Run very slow (I'm guessing due to db shenanigans), but they pass:)
'''

# Test that the method queries the db correctly with a user already in it
def test_check_username_true():
    username = 'test'
    password = 'test'
    
    conn, cursor = connect()
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password)
    
    user = project.User(username)    
    
    try:
        assert user.check_username() == True
    finally:
        revert_database(conn = conn, cursor = cursor)


# Test that the method returns False, when querying for a user not in the database
def test_check_username_false():
    conn, cursor = connect()
    
    user = project.User('test2')
    
    try:
        assert user.check_username() == False
    finally:
        conn.close()
    

# Test the the method correctly handles the password storing when registering
def test_register():
    conn, cursor = connect()
    
    username = 'test3'
    password = 'test3'
    
    user = project.User(username)
        
    with patch('builtins.input', side_effect = [password]):
        user.register(cursor)  

    cursor.execute('SELECT password FROM users WHERE username = ?', (username, ))
    res = cursor.fetchone()[0]
    
    revert_database(conn = conn, cursor = cursor)
    
    assert check_password_hash(res, password) == True
 

# Same, but during login
def test_login():
    conn, cursor = connect()
    
    username = 'test4'
    password = 'test4'
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password)
    
    user = project.User(username)
        
    with patch('builtins.input', side_effect = [password]):
        user.login(cursor)  

    cursor.execute('SELECT password FROM users WHERE username = ?', (username, ))
    res = cursor.fetchone()[0]
    
    revert_database(conn = conn, cursor = cursor)
    
    assert check_password_hash(res, password) == True


'''
Several methods below check how the method get_pet() returns a Tamagotchi object, correctly storing data about it in db
but with different conditions indicated by the test's name. The condition include:
1. No pet in db. New pet created
2. One pet in db. Pet returned
3. One pet in db. New pet created
4. Many pets in db. Chosen pet returned
5. Many pets in db. New pet created
'''
def test_get_pet_no_pet():
    conn, cursor = connect()
    
    username = 'test5'
    password = 'test5'
    names = ['test5']
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password)
    
    user = project.User(username)
    
    with patch('builtins.input', side_effect = [names[0]]):
        pet = user.get_pet(cursor)
    
    cursor.execute('SELECT name FROM tamagotchi WHERE user_id = (SELECT id FROM users WHERE username = ?)', (username, ))
    res = cursor.fetchone()[0]
    
    revert_database(conn = conn, cursor = cursor)
    
    assert res == names[0]
    assert pet.name == names[0]
    assert pet.name == res
        
def test_get_pet_one_pet():
    conn, cursor = connect()

    username = 'test6'
    password = 'test6'
    names = ['test6']
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password, names = names)
    
    user = project.User(username)
    
    with patch('builtins.input', side_effect = [names[0]]):
        pet = user.get_pet(cursor)
        
    cursor.execute('SELECT name FROM tamagotchi WHERE user_id = (SELECT id FROM users WHERE username = ?)', (username, ))
    res = cursor.fetchone()[0]
    
    revert_database(conn = conn, cursor = cursor)
    
    assert res == names[0]
    assert pet.name == names[0]
    assert pet.name == res

def test_get_pet_one_pet_create_new():
    conn, cursor = connect()
    
    username = 'test7'
    password = 'test7'
    names = ['test7']
    new_name = 'new_test7'
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password, names = names)
    
    user = project.User(username)
    
    with patch('builtins.input', side_effect = ['+', new_name]):
        pet = user.get_pet(cursor)
    
    cursor.execute('SELECT name FROM tamagotchi WHERE user_id = (SELECT id FROM users WHERE username = ?)', (username, ))
    results = cursor.fetchall()
    db_names = [result[0] for result in results]
    
    revert_database(conn = conn, cursor = cursor)
    
    assert names[0] == db_names[0]
    assert new_name == db_names[1]
    assert pet.name == new_name
    assert pet.name == db_names[1]


def test_get_pet_many_pets():
    conn, cursor = connect()
    
    username = 'test8'
    password = 'test8'
    names = ['test8_1', 'test8_2', 'test8_3']
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password, names = names)
    
    user = project.User(username)
    
    with patch('builtins.input', side_effect = [names[0]]):
        pet = user.get_pet(cursor)
    
    cursor.execute('SELECT name FROM tamagotchi WHERE user_id = (SELECT id FROM users WHERE username = ?)', (username, ))
    results = cursor.fetchall()
    db_names = [result[0] for result in results]
    
    revert_database(conn = conn, cursor = cursor)
    
    assert names[0] == db_names[0]
    assert names[1] == db_names[1]
    assert names[2] == db_names[2]
    assert pet.name == names[0]
    assert pet.name == db_names[0]


def test_get_pet_many_pets_create_new():
    conn, cursor = connect()
    
    username = 'test9'
    password = 'test9'
    names =['test9_1', 'test9_2', 'test9_3']
    new_name = 'test9_4'
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password, names = names)
    
    user = project.User(username)
    
    with patch('builtins.input', side_effect = ['+', new_name]):
        pet = user.get_pet(cursor)
        
    cursor.execute('SELECT name FROM tamagotchi WHERE user_id = (SELECT id FROM users WHERE username = ?)', (username, ))
    results = cursor.fetchall()
    db_names = [result[0] for result in results]
    
    revert_database(conn = conn, cursor = cursor)
    
    assert new_name == db_names[3]
    assert pet.name == new_name
    assert pet.name == db_names[3]


# Test that due to a save for the current tamagotchi being absent, standard statuses are assigned to the object    
def test_tamagotchi():
    username = 'test5'
    name = 'test5'
    
    test_tamagotchi = project.Tamagotchi(username, name)
    
    assert test_tamagotchi.food == 50
    assert test_tamagotchi.happiness == 50
    assert test_tamagotchi.name == name
    assert test_tamagotchi.username == username


# Test that the save files, created for the previous test (due to code structure of the project) exist in the file and store the correct info    
def test_savefile():
    usernames = ['test5', 'test6', 'test7', 'test8', 'test9']
    names = ['test5', 'test6', 'new_test7', 'test8_1', 'test9_4']
    saves_found = [False for x in range(5)]
    
    for i, (username, name) in enumerate(zip(usernames, names)):
        test_tamagotchi = project.Tamagotchi(username, name)
        
        with open('saves.csv', mode='r') as file:
            reader = csv.DictReader(file)
    
            for row in reader:
                if row['username'] == username and row['name'] == name:
                    saves_found[i] = True
    
    for item in saves_found:
        assert item == True


# Check that update_statuses method returns true or false given all the necessary arguments, and False if arguments are missing    
def test_update_statuses():
    username = 'test10'
    name = 'test10'
    
    food_effect = 10
    happiness_effect = 10
    action = 'feed'
    
    test_tamagotchi = project.Tamagotchi(username, name)
    
    res = test_tamagotchi.update_statuses(food_effect, happiness_effect, action)
    
    action = 'interact'
    
    res_2 = test_tamagotchi.update_statuses(food_effect, happiness_effect, action)
    
    assert res in [True, False]
    assert res_2 in [True, False]
    assert test_tamagotchi.update_statuses() == False
    assert test_tamagotchi.update_statuses(food_effect, happiness_effect) == False


# Check that the method returns True or False with arguments, and False without them
def test_proceed_with_action():
    username = 'test11'
    name = 'test11'
    
    action = 'feed'
    
    test_tamagotchi = project.Tamagotchi(username, name)
    
    res = test_tamagotchi.proceed_with_action(action)
    
    action = 'interact'
    
    res_2 = test_tamagotchi.proceed_with_action(action)
    
    assert res in [True, False]
    assert res_2 in [True, False]
    assert test_tamagotchi.proceed_with_action() == False
    
# Test that both Tamagotchi object gain +10 happiness when this method executes
def test_visit_random():
    username = 'test12'
    password = 'test12'
    name = 'test12'
    
    username_2 = 'test13'
    password_2 = 'test13'
    name_2 = 'test13'
    
    conn, cursor = connect()
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password, names = [name])
    alter_database(conn = conn, cursor = cursor, username = username_2, password = password_2, names = [name_2])
    
    user = project.User(username)
    
    with patch('builtins.input', side_effect = [name, '2']):
        user.tamagotchi = user.get_pet(cursor)
        user.tamagotchi.visit(cursor)
    
    revert_database(conn = conn, cursor = cursor)
    
    with open('saves.csv', mode = 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if row['username'] == username and row['name'] == name:
                assert row['happiness'] == '60'
            if row['username'] == username_2 and row['name'] == name_2:
                assert row['happiness'] == '60'
                
# Same thing, but with a specific user and tamagotchi this time
def test_visit_specific():
    username = 'test14'
    password = 'test14'
    name = 'test14'
    
    username_2 = 'test15'
    password_2 = 'test15'
    name_2 = 'test15'
    
    conn, cursor = connect()
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password, names = [name])
    alter_database(conn = conn, cursor = cursor, username = username_2, password = password_2, names = [name_2])
    
    user = project.User(username)
    
    with patch('builtins.input', side_effect = [name, '1', username_2, name_2]):
        user.tamagotchi = user.get_pet(cursor)
        user.tamagotchi.visit(cursor)
    
    revert_database(conn = conn, cursor = cursor)
    
    with open('saves.csv', mode = 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if row['username'] == username and row['name'] == name:
                assert row['happiness'] == '60'
            if row['username'] == username_2 and row['name'] == name_2:
                assert row['happiness'] == '60'
    
    # End of tests, so delete all the test entries in the save files
    revert_savefile()