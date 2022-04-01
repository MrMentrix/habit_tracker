import json
import datetime
import sys
from time import sleep
import random
import os

class HabitTracker():

    # BASE FUNCTIONS / METHODS

    def __init__(self, name="Jarvis"):
        """This function is used to initialize the Habit Tracker. It will also load existing settings from the settings.json file"""

        self.name = name # giving your habit assistant
        with open('settings.json', 'r+') as settings: # opening the settings file
            settings_file = json.load(settings) # loading the settings file

            if settings_file['first_boot'] == True: # if this is the first boot, walk through the tutorial
                # creating sample habits

                # making sure that folders exist
                if not os.path.exists('habits'):
                    os.makedirs('habits')
                if not os.path.exists('journal'):
                    os.makedirs('journal')

                settings_file['first_boot'] = False # setting first boot to false
                self.create(name="walk", period="day", amount=1)
                self.create(name="drink 2l water", period="day", amount=1)
                self.create(name="gym", period="week", amount=3)
                self.create(name="read a book", period="week", amount=1)
                self.create(name="cook healthy", period="week", amount=5)
                for file in os.listdir("./habits/"): # generating random data
                    with open(f"./habits/{file}", "r+") as f: # opening the habit file
                        data = json.load(f)
    
                        for i in range(random.randint(10,50)):
                            days = random.randint(0,28) # past 4 weeks
                            hours = random.randint(10,22) # between 10 am and pm
                            minutes = random.randint(0,59)
                            seconds = random.randint(0,59)

                            random_timestamp = datetime.datetime.now() - datetime.timedelta(days) # random timestamp
                            random_timestamp = datetime.datetime(random_timestamp.year, random_timestamp.month, random_timestamp.day, hours, minutes, seconds)
                            data['checked'].append(random_timestamp.strftime("%Y-%m-%d %H:%M:%S"))

                        f.seek(0) # resetting file position to beginning
                        json.dump(data, f, indent=4) # saving the json file
                        f.truncate() # get rid of remaining parts
                        f.close()

                self.setup_tour(first_time=True) # running the setup script for introduction to habit tracker
                settings_file['username'] = self.username

            else:
                self.username = settings_file['username']
                self.send_message(f"Hey there, {self.username}! I'm happy to see you again!") # greeting the user

            self.last_streak_update = settings_file['last_streak_update'] # setting the last streak update to the last time it was updated
            settings.seek(0) # resetting file position to beginning
            json.dump(settings_file, settings, indent=4) # saving the json file
            settings.truncate() # get rid of remaining parts
            settings.close()

        self.wait_for_command() # start command loop

    def setup_tour(self, first_time=False):
        """The setup function will only be ran once after initializing the Habit Tracker, giving the user a brief introduction to all the features."""

        # Introduction Messages / Setup Dialogue
        if first_time:
            self.send_message(f"Hello there, my name is {self.name} and I'm here to help you stick to your habits!")
            self.send_message(f"I hope you're having a nice day so far. How do you want to be called?")
            self.send_message("Enter your name:")
            self.username = str(input()) # Getting the users name
            with open('settings.json', 'r+') as f:
                data = json.load(f)
                data['username'] = self.username # changing name value
                f.seek(0) # resetting file position to beginning
                json.dump(data, f, indent=4) # saving the json file
                f.truncate() # get rid of remaining parts
                f.close()
            self.send_message(f"I'm happy to meet you, {self.username}!")

            # skip tutorial
            self.send_message(f"If you're already familiar with how the commands work, feel free to skip the tutorial! You can always re-visit any part of the tutorial by using the 'help' command!")
        self.send_message(f"Do you want me to walk you through the tutorial?")
        if self.yes_or_no() == True:

            self.send_message(f"Alright, let's start with the tutorial!")
            self.send_message(f"I've already created some sample-habits for you. Do you want to take a look at them?")
            
            if self.yes_or_no() == True:
                self.send_message(f"This is the list of your current habits:\n{self.list_habits()}")

            # managing habits
            self.send_message(f"\nDo you want to learn how to set up and manage habits?")
            if self.yes_or_no() == True:
                self.send_message(f"There are a few commands you can manage your habits with. You can use these features by just typing the command.")
                self.send_message(f"The first one is the 'create' command. With this you can create a new habit. You'll be going through a short process to set up your new habit.")
                self.send_message(f"You can change existing habits with the 'modify' command.")
                self.send_message(f"To delete a habit just use the 'delete' command.")
                self.send_message(f"However, if you only want to pause a habit, use 'pause' and 'activate' to manage the status of your habit.")
                self.send_message(f"Note, that pausing a habit will not prevent streaks from being ended when not doing the habit. It's just a way to manage your habits.")
                self.send_message(f"If you want to check off a habit, use the 'check' command.")
                self.send_message(f"You've learned everything there is to know about the habit management!")
                self.send_message(f"wait...", speed=0.15)
                self.send_message(f"There is one more thing!")
                self.send_message(f"You can list all your habits with the 'list' command! It's always good to keep track of your habits!")

            # habit analytics
            self.send_message(f"\nDo you want to learn how to work with your habit analytics?")
            if self.yes_or_no() == True:
                self.send_message(f"You can open a general review of all your habits for a custom period of time by 'review'.")
                self.send_message(f"If you want to open the general overview, use 'overview'.")
                self.send_message(f"By using the 'details' command you can view the analytics of single habits.")

            # journaling
            self.send_message(f"\nDo you want to learn how the journaling works?")
            if self.yes_or_no() == True:
                self.send_message(f"Journaling goes very well with habit tracking, that's why I also offer that feature!")
                self.send_message(f"You can use the 'journal' command to write to the journal.")
                self.send_message(f"You can also use the 'read' command to read from the journal.")
                self.send_message(f"The journal files will be saved with the current date as the file name into the journal folder.")
                self.send_message(f"Therefore you have easy access your journal entries!")
                self.send_message(f"You're also able to write to your journal by just opening the .txt file and writing there!")

        self.send_message(f"That's it! You're good to go now!")
        self.send_message(f"I wish you the best of luck with sticking to your habits and will do my best to help you!\n")

    def wait_for_command(self):
        """The command loop will wait for the user to enter a command and then execute the command."""

        if self.last_streak_update != datetime.datetime.now().strftime("%Y-%m-%d"):
            self.streak()
            self.last_streak_update = datetime.datetime.now().strftime("%Y-%m-%d")
            with open('settings.json', 'r+') as f:
                data = json.load(f)
                data['last_streak_update'] = self.last_streak_update # changing name value
                f.seek(0) # resetting file position to beginning
                json.dump(data, f, indent=4) # saving the json file
                f.truncate() # get rid of remaining parts
                f.close()

        command = input(f"\nEnter a command: | Try: 'commands' & 'help' | Use 'exit' to leave menus and return back here!\n") # open input

        # all command options
        if command == 'commands': print('GENERAL:\ncommands\t| Opens up the command menu\nhelp\t\t| Opens up the help menu\nsettings\t| Opens up the general settings menu\nlist\t\t| Lists all your habits\nHABIT MANAGEMENT:\ncreate\t\t| Create a habit\nmodify\t\t| Edit a habit\ndelete\t\t| Deletes a habit\npause\t\t| Pauses a habit\nactivate\t| Re-Activates a habit\ncheck\t\t| "check off" a habit\nHABIT ANALYTICS:\nreview\t\t| Open a weekly or monthly review\noverview\t| Open your general habit overview\ndetails\t\t| Open detailed analytics of a habit\nJOURNALING:\njournal\t\t| Open your journal menu\nread\t\t| Read from your journal'),
        elif command == 'help': self.setup_tour(),
        elif command == 'settings': self.settings(),
        elif command == 'list': print("OVERVIEW"), print(self.list_habits()),
        elif command == 'create': self.create(),
        elif command == 'modify': self.modify(),
        elif command == 'delete': self.delete(),
        elif command == 'pause': self.pause(),
        elif command == 'activate': self.activate(),
        elif command == 'check': self.check(),
        elif command == 'review': self.review(),
        elif command == "overview": self.overview()
        elif command == 'details': self.details(),
        elif command == 'journal': self.journal(),
        elif command == 'read': self.read(),
        elif command == 'exit': self.send_message(f"There is nothing to exit here...")
        else: self.send_message(f"Oops, I couldn't find the command you're looking for")

        self.wait_for_command()

    def settings(self):
        """This is the settings menu, where you can change the general settings."""
        with open(f'./settings.json', 'r+') as f:
            data = json.load(f)
            speeds = {1: 0.02, 2: 0.0175, 3: 0.015, 4: 0.0125, 5: 0.01, 6: 0.0075, 7: 0.005, 8: 0.0025, 9: 0.001, 10: 0.0005}
            print(f"CURRENT SETTINGS:\nUsername: {data['username']}\nWriting Speed: {list(speeds.keys())[list(speeds.values()).index(data['writing_speed'])]}\n")
            self.send_message("What settings would you like to change?")
            self.send_message("[username, writing speed]")
            selection = input("Enter selection: ")

            if self.exit_check(selection): return
            if selection not in ["username", "writing speed"]:
                self.send_message("Please make a valid selection.")
                selection = input("Enter selection: ")
                if self.exit_check(selection): return

            if selection == "username":
                self.send_message("Please enter a new username:")
                new_username = input()
                if self.exit_check(new_username): return
                data['username'] = new_username
                self.username = new_username

            if selection == "writing speed":
                self.send_message("Please choose a writing speed from 1-10.")
                speed = input("Enter speed: ")
                if self.exit_check(speed): return
                while speed not in speeds: # making sure amount is int
                    error = False
                    try:
                        speed = int(speed)
                    except:
                        error = True
                    if error or speed not in speeds:
                        self.send_message(f"Something went wrong. Please enter a valid number!")
                        self.send_message(f"Enter a number from 1-10:")
                        speed = input("")
                data['writing_speed'] = speeds.get(speed)

            f.seek(0) # resetting file position to beginning
            json.dump(data, f, indent=4) # saving the json file
            f.truncate() # get rid of remaining parts
            f.close()
            if selection == "username": self.send_message(f"Alright, I'll call you {self.username} from now on!")
            if selection == "writing speed": self.send_message("This will be your new writing speed!")

    # BACKGROUND FUNCTIONS / METHODS

    def send_message(self, message="Someone forgot to add a message :(", speed=False):
        """This function sends a message to the user."""
        if not speed:
            with open("./settings.json") as f:
                data = json.load(f)
                speed = data['writing_speed']
                f.close()
        for letter in message:
            sleep(random.uniform(speed*0.2,speed*3)) # random delay between letters to create "tying feeling"
            sys.stdout.write(letter)
            sys.stdout.flush() # giving the illusion of actual writing
        print("")
        sleep(0.5) # short pause after sending message

    def yes_or_no(self):
        """This function asks the user if they want to continue."""
        self.send_message(f"type: 'yes' or 'no'")
        answer = input().lower()
        while answer not in ['yes','yeah', 'sure', 'no', 'nope', 'nah']: # making sure we understand the answer and send an error message if we don't
            self.send_message(random.choice(["Alright, we'll skip that for now.", "Okay, let's just skip this then!"]))
            self.send_message(f"type: 'yes' or 'no'")
            answer = str(input()).lower()
        if answer in ['yes', 'yeah', 'sure']:
            return True
        else:
            return False

    def exit_check(self, input):
        """This function checks if the user wants to exit the menu."""
        if input == "exit":
            print("Exited menu")
            return True
        else:
            return False

    def habits(self):
        """This function returns a list of some habit data."""
        overview = {
            "habits": [],
            "periods": [],
            "amounts": [],
            "status": []
        }

        for file in os.listdir("./habits/"):
            with open(f'./habits/{file}') as f:
                data = json.load(f)
                overview['habits'].append(data['name'])
                overview['periods'].append(data['period'])
                overview['amounts'].append(data['amount'])
                overview['status'].append(data['status'])
                f.close()
        return overview

    def list_habits(self):
        """This function returns a list of all habits, better formated."""
        display_message = ""
        if self.habits()['habits'] == []: return "There are no habits."
        for i in range(len(self.habits()['habits'])): # loop through all habits
            if self.habits()['amounts'][i] == 1: # if period amount is 1, make periods be 'daily', 'weekly' and 'monthly'
                if self.habits()['periods'][i] == "day":
                    period = " daily"
                else:
                    period = f" {self.habits()['periods'][i]}ly"
            else: # create 'x times per period' string
                period = f" {self.habits()['amounts'][i]} times per {self.habits()['periods'][i]}"
            
            # making sure distancing between habit and period is correct
            if(len(self.habits()['habits'][i]) < 8): tab1 = "\t\t\t"
            elif(len(self.habits()['habits'][i]) < 16): tab1 = "\t\t"
            else: tab1 = "\t"
            if(len(period) < 8): tab2 = "\t\t\t"
            elif(len(period) < 16): tab2 = "\t\t"
            else: tab2 = "\t"

            # adding habit with period to display message
            display_message += f"{self.habits()['habits'][i]}{tab1}|{period}{tab2}| {self.habits()['status'][i]}\n"
        return display_message

    def choose_habit(self):
        """This function returns the habit the user wants to work on."""
        print(self.habits()['habits'])
        self.send_message(f"Choose a habit:")
        habit = input().lower()
        if self.exit_check(habit): return "exit"
        while habit not in self.habits()['habits']:
            self.send_message(f"Sorry, I couldn't find a habit called like that. Please try again:")
            habit = input().lower()
            if self.exit_check(habit): return "exit"
        return habit

    def add_file(self, name=False, period=False, amount=False):
        """This function adds a new habit file to the habits folder."""
        if type(name) is not str or type(period) is not str or type(amount) is not int: return # make sure types are correct
        if name in self.habits()['habits']: return # no duplicates

        # making sure that folders exist
        if not os.path.exists('habits'):
            os.makedirs('habits')

        data = {
            "name": name,
            "period": period,
            "amount": amount,
            "status": "active",
            "longest_streak": 0,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "checked": []
        }
        with open(f'./habits/{name}.json', 'w') as f:
            json.dump(data, f, indent=4)
            f.close()

    def streak(self, habit=False):
        """This function returns the current streak of a habit or all habits."""
        files = []
        if not habit:
            for file in os.listdir("./habits/"): # getting all habit files
                if file.endswith(".json"): files.append(file[:-5])

        else:
            files.append(habit)
        streaks = {}
        for file in files:
            with open(f'./habits/{file}.json', 'r+') as f: # loop through all selected files
                data = json.load(f)

                # sorting all dates
                list = sorted([datetime.datetime.fromisoformat(date) for date in data['checked']], reverse=True)
                strf_list = []
                for date in list: strf_list.append(date.strftime("%Y-%m-%d %H:%M:%S"))
                data['checked'] = strf_list
                
                
                now = datetime.datetime.now()
                # getting checks from n days before
                check_counter = [0 for i in range((datetime.datetime.now().date() - datetime.datetime.fromisoformat(data['checked'][-1]).date()).days+1)] # create check counter list
                for check in data['checked']:
                    check_counter[(now.date()-datetime.datetime.fromisoformat(check).date()).days] += 1
                
                # reset streaks if failed, add 1 day if amount is reached
                periods = {'day': 1, 'week': 7, 'month': 30}
                p = periods.get(data['period'])
                streak = 0
                for i in range(len(check_counter)-p+1):
                    summe = sum(check_counter[-(p+i):-i])
                    if sum(check_counter[-(p+i):-i]) >= data['amount']:
                        streak += 1
                        if streak > data['longest_streak']: data['longest_streak'] = streak
                    else:
                        streak = 0
                f.seek(0) # resetting file position to beginning
                json.dump(data, f, indent=4) # saving the json file
                f.truncate() # get rid of remaining parts
                f.close()
            streaks[file] = streak # creating streak dict
        return streaks # returning streak dict

    # GENERAL HABIT COMMANDS

    def create(self, name=False, period=False, amount=False):
        """This function creates a new habit."""
        if not name or not period or not amount: # regular creation
            self.send_message(f"Hey {self.username}! How would you like to name your new habit?")
            self.send_message(f"Enter a name:")
            name = input().lower() # get habit name
            if self.exit_check(name): return
            while name in self.habits()['habits'] or name == 'exit': # making sure name is unique
                self.send_message(f"It seems like you've already added a habit with that name. Please choose another name!")
                name = input().lower()
                if self.exit_check(name): return

            self.send_message(f"The default habit period is 'daily'. Would you like to keep it like that?")
            if self.yes_or_no() == False:
                self.send_message(f"Do you want the tracking period to be daily, weekly or monthly?")
                self.send_message("Enter (d/w/m):")
                period = input().lower() # choosing tracking period
                if self.exit_check(period): return
                while period not in ["d", "w", "m", 'daily', 'weekly', 'monthly']: # making sure period is valid
                    self.send_message("Something went wrong... Make sure to type 'd', 'w' or 'm' to choose your period!")
                    self.send_message("Enter (d/w/m):")
                    period = input().lower()
                    if self.exit_check(period): return

                if period in ['d', 'daily']: period = "day"
                if period in ['w', 'weekly']: period = "week"
                if period in ['m', 'monthly']: period = "month"

                self.send_message(f"How many times per {period} do you want to execute this habit?")
                self.send_message(f"Enter a number")
                amount = input("")
                while type(amount) != int: # making sure amount is int
                    try:
                        amount = int(amount)
                    except:
                        self.send_message(f"Something went wrong. Please enter a valid number!")
                        self.send_message(f"Enter a number:")
                        amount = input("")
            else:
                amount = 1
                period = "day"

            # creating and saving data to json
            self.add_file(name=name, period=period, amount=amount)

            self.send_message(f"I've added your new habit: {name}!\n{amount} time(s) per {period}")
            self.send_message(f"If you want to check this habit off, use the 'check' command!")
            self.send_message(f"Good luck!")
        
        else: # automatic creation
            self.add_file(name=name, period=period, amount=amount)
                          
    def modify(self):
        """This function modifies an existing habit."""
        self.send_message(f"Which habit do you want to modify? Here are your habits:")
        habit = self.choose_habit() # letting user choose a habit
        if self.exit_check(habit): return # exit

        # what to modify
        self.send_message(f"What do you want to modify about this habit?\n(name/period)")
        modification = input().lower()
        if self.exit_check(modification): return
        while modification not in ['name', 'period']: # making sure input is valid
            self.send_message(f"Please enter 'name' or 'period'")
            modification = input().lower()
            if self.exit_check(modification): return
        if modification == 'name': # modifying name
            self.send_message(f"Please enter a new name for this habit:")
            new_name = input().lower()
            if self.exit_check(new_name): return
            if new_name in self.habits()['habits'] or new_name == "exit": # making sure name is unique and not 'exit'
                self.send_message(f"This name is already taken! Please try another one!")
                new_name = input().lower()
                if self.exit_check(new_name): return

            # changing the name
            with open(f'./habits/{habit}.json', 'r+') as f:
                data = json.load(f)
                data['name'] = new_name # changing name value
                f.seek(0) # resetting file position to beginning
                json.dump(data, f, indent=4) # saving the json file
                f.truncate() # get rid of remaining parts
                f.close()
                os.rename(f'./habits/{habit}.json', f'./habits/{new_name}.json') # renaming the file

            self.send_message(f"Alright, I've renamed your habit from '{habit}' to '{new_name}'!")
        
        if modification == 'period': # modifiny period
            self.send_message(f"Do you want the tracking period to be daily, weekly or monthly?")
            self.send_message("Enter (d/w/m):")
            period = input().lower() # choosing tracking period
            if self.exit_check(period): return
            while period not in ["d", "w", "m", 'daily', 'weekly', 'monthly']: # making sure period is valid
                self.send_message("Something went wrong... Make sure to type 'd', 'w' or 'm' to choose your period!")
                self.send_message("Enter (d/w/m):")
                period = input().lower()
                if self.exit_check(period): return

            if period in ['d', 'daily']: period = "day"
            if period in ['w', 'weekly']: period = "week"
            if period in ['m', 'monthly']: period = "month"

            self.send_message(f"How many times per {period} do you want to execute this habit?")
            self.send_message(f"Enter a number")
            amount = input("")
            while type(amount) != int: # making sure amount is int
                try:
                    amount = int(amount)
                except:
                    self.send_message(f"Something went wrong. Please enter a valid number!")
                    self.send_message(f"Enter a number")
                    amount = input("")
            
            with open(f'./habits/{habit}.json', 'r+') as f:
                data = json.load(f)
                data['amount'] = amount # changing amount value
                data['period'] = period # changing amount value
                f.seek(0) # resetting file position to beginning
                json.dump(data, f, indent=4) # saving the json file
                f.truncate() # get rid of remaining parts
                f.close()
            self.send_message(f"Alright, your new habit period is: {amount} time(s) per {period}")

    def delete(self):
        """This function deletes an existing habit."""
        self.send_message(f"Which habit do you want to delete? Here are your habits:")
        habit = self.choose_habit() # choose habit
        if self.exit_check(habit): return # exit

        self.send_message(f"Are you sure that you want to delete the '{habit}' habit?")
        self.send_message(f"Confirm by writing 'yes'.")
        confirm = input().lower()
        if self.exit_check(confirm): return
        if confirm == 'yes': # confirm deletion
            # delete habit
            os.remove(f'./habits/{habit}.json')
            self.send_message(f"You've successfully deleted the habit: {habit}")
        else:
            self.send_message(f"Invalid confirmation! Aborted deletion process.")

    def pause(self):
        """This function pauses an existing habit."""
        self.send_message(f"Choose a habit you want to pause:")
        habit = self.choose_habit() # choosing a habit
        if self.exit_check(habit): return # exit

        if self.habits()['status'][self.habits()['habits'].index(habit)] == "pause": # check if habit is already paused
            return self.send_message(f"This habit is already paused!")

        with open(f'./habits/{habit}.json', 'r+') as f:
            data = json.load(f)
            data['status'] = 'pause' # changing status
            f.seek(0) # resetting file position to beginning
            json.dump(data, f, indent=4) # saving the json file
            f.truncate() # get rid of remaining parts
            f.close()
        self.send_message(f"Your habit '{habit}' is now paused until you activate it again!")

    def activate(self):
        """This function activates a paused habit."""
        self.send_message(f"Choose a habit you want to activate:")
        habit = self.choose_habit() # choosing a habit
        if self.exit_check(habit): return # exit

        if self.habits()['status'][self.habits()['habits'].index(habit)] == "active": # check if habit is already active
            return self.send_message(f"This habit is already active!")

        with open(f'./habits/{habit}.json', 'r+') as f:
            data = json.load(f)
            data['status'] = 'active' # changing status
            f.seek(0) # resetting file position to beginning
            json.dump(data, f, indent=4) # saving the json file
            f.truncate() # get rid of remaining parts
            f.close()
        self.send_message(f"Your habit '{habit}' is now activated again!")

    def check(self):
        """This function checks off a habit."""
        self.send_message(f"Choose a habit you want to check off")
        habit = self.choose_habit() # choosing the habit
        if self.exit_check(habit): return # exit
        with open(f'./habits/{habit}.json', 'r+') as f:
            data = json.load(f)
            # check if habit is already completed
            day_diffs = {"day": 1, "week": 7, "month": 30}
            day_diff = day_diffs.get(data['period'])
            check_amount = 0
            for check in data['checked']:
                timestamp = datetime.datetime.fromisoformat(check)
                if (datetime.datetime.now().date()-timestamp.date()).days < day_diff: # add all checks of running period
                    check_amount += 1
            if check_amount == data['amount']: # goal already completed
                self.send_message(f"You've already completed this habit goal!")
                self.send_message(f"I'll add your check anyways, {self.username}!")
            
            data['checked'].append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            f.seek(0) # resetting file position to beginning
            json.dump(data, f, indent=4) # saving the json file
            f.truncate() # get rid of remaining parts
            f.close()
            
            
            if check_amount+1 == data['amount']: # goal completed
                return self.send_message(f"Congratulations, you've completed your {habit} goal!")

            if check_amount+1 < data['amount']: # goal not completed yet
                return self.send_message(f"Good job, {self.username}! You're on your way! Execute this habit {data['amount']-(check_amount+1)} more times and you're finished!")

    # ANALYZING COMMANDS

    def review(self):
        """Function to create a custom reviews of a selected period of time"""
        self.send_message(f"What period would you like to get a review of?")
        self.send_message(f"type: (d/w/m)")
        period = input().lower()
        if self.exit_check(period): return
        if period not in ["d", "day", "days", "w", "week", "weeks", "m", "month", "months"]:
            self.send_message("Please select a valid period.")
            period = input().lower()
            if self.exit_check(period): return

        period_names = {"d": "days", "day": "days", "days": "days", "w": "weeks", "week": "weeks", "weeks": "weeks", "m": "months", "month": "months", "months": "months"}

        self.send_message(f"How many {period_names.get(period)} do you want your period to be? (Maximum of 90 days)")
        self.send_message(f"Enter a number:")
        amount = input().lower()
        if self.exit_check(amount): return
        while type(amount) != int: # making sure amount is int
            try:
                amount = int(amount)
            except:
                self.send_message(f"Something went wrong. Please enter a valid number!")
                self.send_message(f"Enter a number")
                amount = input("")
        
        period_days = {"d": 1, "day": 1, "days": 1, "w": 7, "week": 7, "weeks": 7, "m": 30, "month": 30, "months": 30}
        days = period_days.get(period)*amount # calculating amount of days
        if days >= 90: days = 90 # making sure max amount is 90 days

        final_message = "HABIT \t\t\t| <- RECENT - OLD -> \t| PERCENTAGE \t| STREAK\n"
        for file in os.listdir("./habits/"):
            with open(f'./habits/{file}', 'r') as f: # loop through all selected files
                data = json.load(f)
                f.close()
                period = data['period']
                amount = data['amount']
                now = datetime.datetime.now()

                # getting checks from n days before
                check_counter = [0 for i in range(days+1)]
                for check in data['checked']:
                    if (now.date()-datetime.datetime.fromisoformat(check).date()).days > days: continue # skip everything more than a month old
                    check_counter[(now.date()-datetime.datetime.fromisoformat(check).date()).days] += 1
                
                # creating the habit review strings
                periods = {'day': 1, 'week': 7, 'month': 30}
                p = periods.get(period)
                i = 0
                habit_string = f"{file[:-5]}"
                # indenting
                if len(habit_string) < 8: habit_string += "\t\t\t| "
                elif len(habit_string) < 16: habit_string += "\t\t| "
                else: habit_string += "\t| "
                achieved = 0
                if i >= days-p:
                    habit_string += "period too short for data to be displayed!"
                while i <= days-p:
                    reached = sum(check_counter[i:i+p])
                    if reached >= amount:
                        habit_string += "X"
                        achieved += 1
                    else:
                        habit_string += "O"
                    i += 1
                if i == 0: i = 1 # avoid ZeroDivisionError

                # adding the streak and completion percentage
                streak = self.streak(file[:-5])
                habit_string += f" | {round((achieved/i)*100)}% \t| Streak: {streak[file[:-5]]}\n"
            final_message += habit_string
        self.send_message(final_message)

    def overview(self):
        """Function to create a overview of all habits"""
        overview_string = "GENERAL HABIT OVERVIEW:\n"
        self.streak() # making sure the streak is up to date and saved to the habit file before loading the file
        for file in os.listdir("./habits/"): # looping through all habits
            with open(f"./habits/{file}", "r") as f:
                data = json.load(f)
                f.close()
                overview_string += f"{data['name']}"
                # indenting 
                if len(data['name']) < 8: overview_string += "\t\t\t| "
                elif len(data['name']) < 16: overview_string += "\t\t| "
                else: overview_string += "\t| "
                
            overview_string += f"Created at: {data['created_at']}\t| Current Streak: {self.streak(file[:-5])[file[:-5]]}\t| Longest Streak: {data['longest_streak']}\n"

        print(overview_string)
    
    def details(self):
        """Function to get details about a selected habit"""
        self.send_message(f"What habit would you like to get details about?")
        habit = self.choose_habit()
        if self.exit_check(habit): return

        with open(f"./habits/{habit}.json", "r") as f:
            data = json.load(f)
            f.close()
        print(f"Habit: {data['name']}")
        print(f"Created at: {data['created_at']}")
        print(f"Period: {data['period']}")
        print(f"Amount (per period): {data['amount']}")
        print(f"Current streak: {self.streak(habit)[habit]}")
        print(f"Longest streak: {data['longest_streak']}")
        print(f"Checked: {data['checked']}")

    # JOURNALING COMMANDS

    def journal(self):
        """Function to create a journal entry"""
        # making sure that folders exist
        if not os.path.exists('journal'):
            os.makedirs('journal')
        entry = input("Enter your entry:\n") # getting the entry
        if self.exit_check(entry): return # checking if the user wants to exit
        with open(f"./journal/{datetime.datetime.now().date()}.txt", "a") as f: # opening the journal file
            f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {entry}\n") # writing the entry to the file
            f.close()
        self.send_message(f"Journal entry saved! You can find it in the journal folder.")

    def read(self):
        """Function to read a journal entry"""
        self.send_message(f"What day would you like to read? Format: YYYY-MM-DD")
        date = input()
        if self.exit_check(date): return
        while type(date) != datetime.date: # making sure date is datetime.date
            try:
                date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            except:
                self.send_message(f"Something went wrong. Please enter a valid date!")
                self.send_message(f"Enter a date")
                date = input("")
        if f"{date.strftime('%Y-%m-%d')}.txt" not in os.listdir("./journal/"): return self.send_message("I couldn't find a journal entry for that day.") # checking if the journal file exists
        with open(f"./journal/{date.strftime('%Y-%m-%d')}.txt", "r") as f: # opening the journal file
            data = f.read()
            f.close()
        self.send_message(f"Journal entry for {date.strftime('%Y-%m-%d')}:") # sending the journal entry
        print(data)

Tracker = HabitTracker()