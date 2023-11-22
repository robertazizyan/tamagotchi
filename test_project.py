import project
import pytest
import sqlite3
from unittest.mock import patch
from werkzeug.security import generate_password_hash, check_password_hash


username = 'test'
password = 'test'
name = 'test'


def connect():
    try:
        conn = sqlite3.connect('database_test.db')
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(e)
        exit()
        
def alter_database(username: str, password: str, name: str):
    conn, cursor = connect()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    cursor.execute('INSERT INTO tamagotchi (user_id, name) VALUES ((SELECT id FROM users WHERE username = ?), ?)', (username, name))
    conn.commit()
    conn.close()


def revert_database(username: str, name: str):
    conn, cursor = connect()
    cursor.execute('DELETE FROM users WHERE username = ?', (username, ))
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


def test_check_username_():
    conn, cursor = connect()
    
    alter_database(username, password, name)
    
    user = project.User(username)
    cursor.execute('SELECT * FROM users WHERE username = ?', (user.username, ))
    res = cursor.fetchone()
    print(res)    
    assert user.check_username() == True
    
    revert_database(username, name)
    
    user_2 = project.User(username)
    cursor.execute('SELECT * FROM users WHERE username = ?', (user_2.username, ))
    res_2 = cursor.fetchone()
    print(res_2)
    print(user_2.check_username())
    assert user_2.check_username() == False

    
    