import project
import pytest
import sqlite3
from unittest.mock import patch


try:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(e)
    exit()


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

def test_User():
    with patch('builtins.input', side_effect=['test']):
        existing_user = project.User('test')
    
    