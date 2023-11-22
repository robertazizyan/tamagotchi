import datetime
import time
import os
import sqlite3
import csv
import random
from sys import exit
from werkzeug.security import check_password_hash, generate_password_hash
from pyfiglet import Figlet
from tabulate import tabulate
import images


figlet = Figlet()


try:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(e)
    exit()


class User:
    def __init__(self, username):
        self.username = username
            
    # Checks whether a username is in the users table of the database and returns a bool
    def check_username(self) -> bool:
        cursor.execute('SELECT * FROM users WHERE username = ?', (self.username, ))
        res = cursor.fetchone()
        
        if not res:
            animated_print('It seems you are not registered yet. To register enter your password below')
            return False
        
        return True
    
    # Insert a new user into the users table from the database
    def register(self) -> None:
        while True:
            password = input('Password: ')
            if password:
                break
            
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (self.username, generate_password_hash(password)))
        
        animated_print(f'Welcome, {self.username}!')
        time.sleep(2)
        
    # Check the password in the users table from the database, if incorrect password is provided force the user to try again
    def login(self) -> None:
        animated_print('To login, enter your password below')
        
        while True:
            password = input('Password: ')
            
            cursor.execute('SELECT password FROM users WHERE username = ?', (self.username, ))
            
            if check_password_hash(cursor.fetchone()[0], password):
                animated_print(f'Welcome back, {self.username}!')
                time.sleep(2)
                break
            else:
                animated_print('Incorrect password. Try again!')  
    
    # returns a Tamagotchi object based on the user already having a Tamagotchi, or not having it(thus creating it through create_pet)
    def get_pet(self):
        clear_terminal()
        
        cursor.execute('SELECT name FROM tamagotchi WHERE user_id = (SELECT id FROM users where username = ?)', (self.username, ))
        pets = cursor.fetchall()
        pet_names = [pet[0] for pet in pets]
        
        if not pet_names:
            animated_print("It seems you currently don't have any Tamagotchi. Let's create one!")
            pet = self.create_pet(pet_names)
        elif len(pet_names) > 1:
            animated_print("It seems you currently have several active Tamagotchi. Let's choose the one you want to play with!") 
            
            print()
            for pet_name in pet_names:
                animated_print(f'{pet_name}')
            print()
                
            animated_print("Which Tamagotchi do you choose? You can also enter '+' to create a new Tamagotchi")
            
            while True:
                name = input('Name or +: ')
                
                if name == '+':
                    pet = self.create_pet(pet_names)
                    break
                
                if name not in pet_names:
                    animated_print('No such Tamagotchi. Try again!')
                else:
                    pet = Tamagotchi(self.username, name)
                    break
                
        else:
            name = pets[0][0]
            animated_print(f"You can choose {name} or enter '+' to create a new Tamagochi.")
            
            while True:    
                confirm_name = input('Name or +: ')
                
                if confirm_name == '+':
                    pet = self.create_pet(pets[0])
                    break
                elif confirm_name == name:
                    pet = Tamagotchi(self.username, name)
                    break
                else:
                    animated_print('Invalid choice. Try again!')
        
        conn.commit()    
        return pet
            
    # Create and add the newly created Tamagotchi object into the database and return it to get_pet method
    def create_pet(self, pet_names: list):
            animated_print("Enter your Tamagotchi's name below. Remember that you won't be able to change it.")
            
            while True:
                name = input("Tamagotchi name: ") 
                if not name:
                    continue
                   
                if name not in pet_names:
                    cursor.execute('INSERT INTO tamagotchi (name, user_id) VALUES(?, (SELECT id FROM users WHERE username = ?))', (name, self.username))
                    pet = Tamagotchi(self.username, name)
            
                    return pet
                else:
                    animated_print('That name is already taken. Try again!')
    

class Tamagotchi:
    # Create a Tamagotchi object, assign statuses, available food, interactions
    def __init__(self, username, name):
        self.username = username
        self.name = name
        self.load_data()
        self.save_data()
     
    # Read the csv file for the saves, if save data was found, call the simulate_time_passage method for the statuses to update, otherwise assign initial values
    def load_data(self) -> None:
        try:
            with open('saves.csv', mode='r') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if row['username'] == self.username and row['name'] == self.name:
                        self.food, self.happiness = self.simulate_time_passage(int(row['food']), int(row['happiness']), datetime.datetime.strptime(row['last_used'], '%Y-%m-%d %H:%M:%S.%f'))
                        self.birthday = datetime.datetime.strptime(row['birthday'], '%Y-%m-%d %H:%M:%S.%f')
                        
                        return
        except FileNotFoundError:
            exit("Couldn't find the csv save file")
    
        self.food = 50
        self.happiness = 50
        self.birthday = datetime.datetime.utcnow()
    
    # Adjust statuses based on the time the user was absent and return it to load_data
    def simulate_time_passage(self, last_food: int, last_happiness: int, last_used: datetime) -> tuple:
        time_passed = datetime.datetime.utcnow() - last_used
        
        hours = time_passed.total_seconds() / (60 **2)
        sleep_time = time_passed.days * 8
        if hours < 1:
            hours = 0
            sleep_time = 0
        hours_to_simulate = hours - sleep_time
        
        current_food = min_max(int(last_food - hours_to_simulate / 2))
        current_happiness = min_max(int(last_happiness - hours_to_simulate / 2))
        
        return current_food, current_happiness
     
    # Update the save in the csv file to store the latest statuses (called in every consequent Tamagotchi method to save data after the action automatically)     
    def save_data(self) -> None:
        data = []
        save_found = False
        current_time = datetime.datetime.utcnow()        

        try:
            # First append all the saves to an empty list, and if a save for the current Tamagotchi is present, append it to the list with the latest statuses
            with open('saves.csv', mode = 'r+', newline = '') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                for row in reader:
                    if row['username'] == self.username and row['name'] == self.name:
                        row['food'] = self.food
                        row['happiness'] = self.happiness
                        row['last_used'] = current_time
                        save_found = True
                        
                    data.append(row)
                    
                # Then rewrite the csv file with the list of data
                file.seek(0)
                writer = csv.DictWriter(file, fieldnames = headers)
                writer.writeheader()
                writer.writerows(data)
            
            # Finally if the save for the current Tamagothci wasn't found in the original csv, write an additional line with the latest statuses      
            if not save_found:
                with open('saves.csv', mode = 'a', newline = '') as file:
                    writer = csv.writer(file)
                    writer.writerow([self.username, self.name, self.food, self.happiness, self.birthday, current_time])
        except FileNotFoundError:
            exit("Couldn't find the csv save file")

    # Calculate the current age of the Tamagotchi in days
    def get_age(self) -> int:
        age = datetime.datetime.utcnow() - self.birthday
        return age.days
    
    # Determine whether the Tamagotchi wants to do what you propose, based on its statuses and its age. Return a bool with the result.
    def proceed_with_action(self, action: str) -> bool:
        success_probability = 100 
        
        if action == 'feed':
            success_probability += int(self.happiness / 5) - self.food - int(self.get_age() / 5)
        elif action ==  'interact':
            success_probability += int(self.food / 5) - self.happiness - int(self.get_age() / 5)
        else:
            return False
        
        if random.randint(0, 100) <= min_max(success_probability):
            return True
        
        return False
    
    # Update the statuses after an action, if the action has been performed successfully via the proceed_with_action method    
    def update_statuses(self, food_effect = 0, happiness_effect = 0, action = 'None') -> bool:
        if self.proceed_with_action(action):
            self.food = min_max(self.food + int(food_effect))
            self.happiness = min_max(self.happiness + int(happiness_effect))
            self.save_data()
            
            return True
        else:
            self.save_data()
            
            return False
            
    
    # Fetch a tamagotchi from the database  either randomly or by user's choice, create its object, update happiness for both Tamagotchi and save the data for both objects    
    def visit(self) -> None:
        
        self.display(status = 'static')
        animated_print('You can input "1" to visit a specific tamagotchi or "2" to visit a random one')
        
        while True:    
            inpt = input('Your choice: ')
            if inpt == '1':
                friend_username, pet_name = self.get_specific_pet()
                break
            elif inpt == '2':
                friend_username, pet_name = self.get_random_pet()
                break
            else:
                animated_print('Invalid choice. Try again!')
        
        friend = Tamagotchi(friend_username, pet_name)

        self.happiness = min_max(self.happiness + 10)
        friend.happiness = min_max(self.happiness + 10)
        
        
        self.display(times = 5, status = 'dynamic', visit = True, friend = friend.name)
        animated_print(f"{self.username}'s {self.name} visits {friend.username}'s {friend.name}!")
        animated_print(f"{self.name}'s and {friend.name}'s happiness increased by 10!")
        
        self.save_data()
        friend.save_data()
        
        time.sleep(3)
    
    # Fetch a specific Tamagotchi from the database, return the username and name of the Tamagotchi
    def get_specific_pet(self) -> tuple:
        while True:
            friend_username = input("Enter your friend's username: ")    
            cursor.execute('SELECT id, username FROM users WHERE username = ?', (friend_username, ))
            friend_user = cursor.fetchone()
            
            if not friend_user:
                animated_print('No such user, try again!')
            elif friend_username == self.username:
                animated_print("Nope. Can't visit yourself!")
            else:
                break
        
        while True:
            pet_name = input(f"Enter {friend_username}'s Tamagotchi name: ")
            cursor.execute('SELECT name FROM tamagotchi WHERE user_id = ? and name = ?', (friend_user[0], pet_name))
            friend_pet = cursor.fetchone()
            
            if not friend_pet:
                animated_print(f'User {friend_username} has no such Tamagotchi. Try again!')
            else:
                break
        
        return friend_user[1], friend_pet[0]

    # Fetch a random Tamagotchi from the database, return a username and name for 
    def get_random_pet(self) -> tuple:
        cursor.execute('SELECT id, username FROM users WHERE username != ?', (self.username, ))
        users = cursor.fetchall()
        id_pos = random.randint(0, len(users) - 1)
        friend_id = users[id_pos][0]
        friend_username = users[id_pos][1]
        cursor.execute('SELECT name FROM tamagotchi WHERE user_id = ?', (friend_id, ))
        pets = cursor.fetchall()
        pet_name = pets[random.randint(0, len(pets) - 1)][0]
        
        return friend_username, pet_name
        
    # Print out a tamagochi animation based on its age, times to display,static or dynamic display and visiting status
    def display(self, times = 1, status = 'dynamic', visit = False, friend = None) -> None:
        age = self.get_age()
        
        if not friend:
            name = figlet.renderText(self.name)
        else:
            name = figlet.renderText(self.name + '  and  ' + friend)
            
        if age < 2:
            image_1 = images.image_1_egg
            image_2 = images.image_2_egg
            image_3 = images.image_3_egg
        else:
            if visit == False:
                image_1 = images.image_1_grown
                image_2 = images.image_2_grown
                image_3 = images.image_3_grown
            else:
                image_1 = images.image_1_visit
                image_2 = images.image_2_visit
                image_3 = images.image_3_visit
                
        image_list = [image_1, image_2, image_3, image_2]  
            
        if status == 'dynamic':
            for i in range(times):
                for item in image_list:
                    clear_terminal()
                    print(name)
                    print(item)
                    time.sleep(0.15)

        elif status == 'static':
            clear_terminal()
            print(figlet.renderText(self.name))
            print(image_2)
            

              
def main():
    
    clear_terminal()
    animated_print('Welcome to my own implementation of the Tamagochi game!\nYou can find the instructions to the game at README.MD\nTo start/continue playing with your Tamagotchi, enter your username below')
    
    while True:
        username = input('Username: ')
        if username:
            break
        
    user = User(username)
    
    if user.check_username():
        user.login()
    else:
        user.register()  
        
    user.tamagotchi = user.get_pet()

    while True:
        user.tamagotchi.display(times = 3, status = 'dynamic')
        show_main_menu(user)

    
# Display main menu and call the chosen method    
def show_main_menu(user: User) -> None:
    menu = [
        ['Index', 'Action', 'Description'],
        ['1', 'Feed', 'Choose the available food and feed them to your Tamagochi' ],
        ['2', 'Interact', f'Choose the available interaction with {user.tamagotchi.name}'],
        ['3', 'Visit another Tamagotchi', "Go play with somebody else's Tamagotchi "],
        ['4', 'Change Tamagotchi', f'Change {user.tamagotchi.name} to other Tamagotchi that you have'],
        ['5', 'Exit', 'Save your progress and exit the game']
    ]
    main_menu = tabulate(menu[1:], headers = menu[0], tablefmt = 'fancy_grid')
    
    hidden_menu = {
        '1': show_food_menu,
        '2': show_interaction_menu,
        '5': game_exit
    }
    
    show_status_menu(user)
    print(main_menu)
    animated_print('Choose an action by inputting the index below')
    
    while True:
        choice = input('Choice: ')
        
        if choice in hidden_menu.keys():
            hidden_menu[choice](user)
            break
        elif choice == '3':
            age = user.tamagotchi.get_age()
            if age < 2:
                animated_print('Your Tamagotchi has to grow up a little before he can visit friends!')
                time.sleep(2)  
                break
            else:  
                user.tamagotchi.visit()
                break
        elif choice == '4':
            user.tamagotchi = user.get_pet()
            break
        else:
            animated_print('Invalid choice. Try again')


# Display food menu and call the feed method based on the user choice            
def show_food_menu(user: User) -> None:
    food = [
        ['Index', 'Type of food', 'Food effect', 'Happiness effect'],
        [1, 'Meat', '+30', '+10'],
        [2, 'Veggies', '+10', '-5'],
        [3, 'Treats', '+10', '+20'],
    ]
    food_menu = tabulate(food[1:], headers = food[0], tablefmt = 'fancy_grid')
    
    user.tamagotchi.display(status = 'static')
    show_status_menu(user)
    print(food_menu)
    animated_print(f'What would you like to feed to {user.tamagotchi.name}? Input the index from the table to make a choice!')
    
    while True:               
        choice = input('Choice: ')
        
        try:
            choice = int(choice)
        except ValueError:
            animated_print('Invalid choice. Try again!')
            continue
        
        if 1 <= choice <= len(food) - 1:       
            if user.tamagotchi.update_statuses(food[choice][2], food[choice][3], 'feed'):
                user.tamagotchi.display(status = 'static')
                show_status_menu(user)
                animated_print(f'You fed {user.tamagotchi.name} with {food[choice][1].lower()}!')
                animated_print(f'Food: {food[choice][2]}')
                animated_print(f'Happiness: {food[choice][3]}')
                
                time.sleep(2)
                break
            else:
                user.tamagotchi.display(status = 'static')
                show_status_menu(user)
                animated_print(f"Looks like {user.tamagotchi.name} doesn't want eat right now:(")
                animated_print("Try again later or try raising its happiness!")
                
                time.sleep(2)
                break                
        else:
            animated_print('Invalid choice. Try again!')
    

# Display the interaction menu and call the interact method based on the user choice    
def show_interaction_menu(user: User) -> None:
    interaction = [
        ['Index', 'Interaction', 'Food effect', 'Happiness effect'],
        [1, 'Pet', '+0', '+5'],
        [2, 'Play with', '-10', '+10'],
        [3, 'Walk', '-20', '+20'],
        [4, 'Clean', '+0', '-10']
    ]
    interaction_menu = tabulate(interaction[1:], headers = interaction[0], tablefmt = 'fancy_grid')
    
    user.tamagotchi.display(status = 'static')
    show_status_menu(user)
    print(interaction_menu)
    animated_print(f'How would you like to interact with {user.tamagotchi.name}? Input the index from the table to make a choice!')
    
    while True:
        choice = input('Choice: ')
        
        try:
            choice = int(choice)
        except ValueError:
            animated_print('Invalid choice. Try again!')
            continue
        
        if 1 <= choice <= len(interaction) - 1:
            if user.tamagotchi.update_statuses(interaction[choice][2], interaction[choice][3], 'interact'):
                user.tamagotchi.display(status = 'static')
                show_status_menu(user)
                animated_print(f'You {interaction[choice][1].lower()} {user.tamagotchi.name}!')
                animated_print(f'Food: {interaction[choice][2]}')
                animated_print(f'Happiness: {interaction[choice][3]}')
                
                time.sleep(2)
                break
            else:
                user.tamagotchi.display(status = 'static')
                show_status_menu(user)
                animated_print(f"Looks like {user.tamagotchi.name} doesn't want to do that right now:(")
                animated_print("Try again later or try feeding it!")
                
                time.sleep(2)
                break
        else:
            animated_print('Invalid choice. Try again!')   


# Show status_menu
def show_status_menu(user: User) -> None:
    statuses = [
        ['Food', 'Happiness'],
        [f'{user.tamagotchi.food} / 100', f'{user.tamagotchi.happiness} / 100']
    ]
    statuses_menu = tabulate(statuses[1:], headers = statuses[0], tablefmt = 'fancy_grid')
    
    print(statuses_menu)


# Save the data, close the database and exit the program    
def game_exit(user: User) -> None:
    user.tamagotchi.display(times = 3, status = 'dynamic')
    user.tamagotchi.save_data()
    conn.close()
    exit('See you next time!')
    

# Caps the statuses of the tamagotchi between 0 and 100
def min_max(status: int) -> int:
    return max(0, min(100, status))


# Self explanatory            
def clear_terminal() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
    

def animated_print(text: str) -> None:
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.02)   
    print()    


if __name__ == '__main__':
    main()   