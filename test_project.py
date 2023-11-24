import project
import pytest
import sqlite3
from unittest.mock import patch
from werkzeug.security import generate_password_hash, check_password_hash


def connect():
    try:
        conn = sqlite3.connect('database_test.db')
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(e)
        exit()
        
def alter_database(conn, cursor, username = None, password = None, name = None):
    if username and password:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, generate_password_hash(password)))
        
    if username and name:
        cursor.execute('INSERT INTO tamagotchi (user_id, name) VALUES ((SELECT id FROM users WHERE username = ?), ?)', (username, name))
    
    conn.commit()


def revert_database(conn, cursor, username = None, name = None):
    if username:
        cursor.execute('DELETE FROM users WHERE username = ?', (username, ))
    
    if name:
        cursor.execute('DELETE FROM tamagotchi WHERE name = ?', (name, ))
        
    conn.commit()
    conn.close()
    
    
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


def test_min_max():
    assert project.min_max(0) == 0
    assert project.min_max(100) == 100
    assert project.min_max(-1) == 0
    assert project.min_max(101) == 100
    assert project.min_max(50) == 50


def test_clear_terminal():
    assert project.clear_terminal() == None


def test_animated_print():
    assert project.animated_print('hello') == None
    
    with pytest.raises(TypeError):
        project.animated_print(123)
        
    with pytest.raises(TypeError):
        project.animated_print()


def test_check_username_true():
    username = 'test'
    password = 'test'
    name = 'test'
    
    conn, cursor = connect()
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password)
    
    user = project.User(username)    
    
    try:
        assert user.check_username() == True
    finally:
        revert_database(conn = conn, cursor = cursor, username = username)


def test_check_username_false():
    conn, cursor = connect()
    
    user = project.User('test2')
    
    try:
        assert user.check_username() == False
    finally:
        conn.close()
    

def test_register():
    conn, cursor = connect()
    
    username = 'test3'
    password = 'test3'
    
    user = project.User(username)
        
    with patch('builtins.input', side_effect = [password]):
        user.register(cursor)  

    cursor.execute('SELECT password FROM users WHERE username = ?', (username, ))
    res = cursor.fetchone()[0]
    
    revert_database(conn = conn, cursor = cursor, username = username)
    
    assert check_password_hash(res, password) == True
 

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
    
    revert_database(conn = conn, cursor = cursor, username = username)
    
    assert check_password_hash(res, password) == True


def test_get_pet_and_create_pet_no_pet():
    conn, cursor = connect()
    
    username = 'test5'
    password = 'test5'
    name ='test5'
    
    alter_database(conn = conn, cursor = cursor, username = username, password = password)
    
    user = project.User(username)
    
    with patch('builtins.input', side_effect = [name]):
        pet = user.get_pet(cursor)
    
    cursor.execute('SELECT name FROM tamagotchi WHERE user_id = (SELECT id FROM users WHERE username = ?)', (username, ))
    res = cursor.fetchone()[0]
    
    revert_database(conn = conn, cursor = cursor, username = username, name = name)
    
    assert res == name
    assert pet.name == name
    assert pet.name == res
        
def test_get_pet_and_create_pet_one_pet():
    conn, cursor = connect()

    username = 'test6'
    password = 'test6'
    name = 'test6'
    
        
    