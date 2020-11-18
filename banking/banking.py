# Import necessary modules
# To generate random credits card numbers and pins I will use random module
import random
# For this project i will be using SQLite database which comes with standard python installation
import sqlite3

# connection object which will create and/or connect to sqlite3 database file
connection = sqlite3.connect('card.s3db')
print("connected to database...")

# create a cursor object to perform sql queries
cursor = connection.cursor()

# Create a table of card template
table_creation = """
                 CREATE TABLE IF NOT EXISTS card (
                                        id INTEGER PRIMARY KEY,
                                        number TEXT,
                                        pin TEXT,
                                        balance INTEGER DEFAULT 0
                                    );
                 """

# Execute creating table in case it was not previously created
cursor.execute(table_creation)


# Insert a record of card into the database table using custom function
def insert_into_table(card_num, card_pin):
    try:
        sqlite_insert_with_param = """
                                    INSERT INTO card
                                    (number,pin)
                                    VALUES (?,?);
                """
        data_tuple = (card_num, card_pin)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        connection.commit()
        print("Your card has been created")
        print("Your card number:")
        print(card_num)
        print("Your card PIN:")
        print(card_pin)
    except sqlite3.Error as error:
        print('Failed to insert data', error)


# Searching in the database table using custom function
def search_in_table(search_card, search_pin):
    try:
        cursor.execute("SELECT number,pin, balance FROM card WHERE number=? AND pin=?", (search_card, search_pin))
        return cursor.fetchone()
    except sqlite3.Error as error:
        print("Could not search the table", error)
        return None


# Update income by adding to balance custom function
def add_income(user):
    try:
        income = -1
        # Check if income is positive
        while True:
            print('Enter Valid income:')
            income = int(input())
            if income >= 0:
                break
        # change balance of the user user[0]=card_number,user[1]=pin and user[2]=balance
        balance = user[2] + income
        card_num = user[0]
        card_pin = user[1]
        # update balance in database
        cursor.execute("UPDATE card SET balance=? WHERE number=? AND pin=?;", (balance, card_num, card_pin))
        # committing to make effect permanent
        connection.commit()
        print('Income was added!')
    except sqlite3.Error as error:
        print('Income could not be added', error)


# transfer from logged in account to another valid account using custom function
# this function checks if input amount and the card to which transfer to be made are valid
def do_transfer(user):
    print('Enter card number:')
    target_card = input()
    if str(target_card) == user[0]:
        print("You can't transfer money to the same account!")
        return
    if not is_valid_luhn(target_card):
        print('Probably you made a mistake in the card number. Please try again!')
        return

    try:
        cursor.execute("SELECT * FROM card WHERE number=? ;", (target_card,))
        if cursor.fetchone() is None:
            print('Such a card does not exist.')
            return
        else:
            print("Enter how much money you want to transfer:")
            transfer_amt = int(input())
            if user[2] < transfer_amt:
                print("Not enough money!")
                return
            else:
                balance = user[2] - transfer_amt
                cursor.execute("UPDATE card SET balance=? WHERE number=? AND pin=?", (balance, user[0], user[1]))
                connection.commit()
                cursor.execute("SELECT balance,number FROM card WHERE number=?", (target_card,))
                target_user = cursor.fetchone()
                target_balance = transfer_amt + target_user[0]
                cursor.execute("UPDATE card SET balance=? WHERE number=?", (target_balance, target_card))
                connection.commit()
                print("Success !")

    except sqlite3.Error as error:
        print(error)


# When a card record to be removed permanently from the database, this function will clear all the data
# of that particular card
def close_acc(user):
    cursor.execute("DELETE FROM card WHERE number=?", (user[0],))
    connection.commit()


# Check if the given card number is a valid luhn number
def is_valid_luhn(card_number) -> bool:
    all_digit = [int(x) for x in list(card_number)]
    sums = 0
    # Luhn Algorithm
    for i in range(len(all_digit)):
        if i % 2 == 0:
            if 2 * all_digit[i] > 9:
                sums += (2 * all_digit[i] - 9)
            else:
                sums += 2 * all_digit[i]
        else:
            sums += all_digit[i]
    if sums % 10 == 0:
        return True
    else:
        return False


# This function will create an unused valid credit card number
def luhn_num():
    # Query to get all numbers present in database
    cursor.execute("SELECT number FROM card")
    used = cursor.fetchall()
    while True:
        num = random.randint(4000000000000000, 4000010000000000 - 1)
        if num in used:
            continue
        if is_valid_luhn(str(num)):
            return str(num)


# Generate 4 digit pin which of format dddd and return as string
def gen_pin():
    pins = ["%04d" % x for x in range(10000)]
    return random.choice(pins)


# Main menu template
Main_Menu = """
1. Create an account
2. Log into account
0. Exit
"""

# User menu template
User_Menu = """
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
"""


def main():
    while True:
        print(Main_Menu)
        response = str(input())
        if response == "1":
            l_num = luhn_num()
            g_pin = gen_pin()
            insert_into_table(l_num, g_pin)
            # x = BankAcc()

        elif response == "2":
            # log_in()
            print("Enter your card number:")
            tmp_num = str(input())
            print("Enter your PIN:")
            tmp_pin = str(input())
            # user = cursor.execute("SELECT * FROM card WHERE SUBSTRING(tmp_num, 1, 17)=number;")
            user = search_in_table(tmp_num, tmp_pin)
            if user is not None:
                print("You have successfully logged in!")
            if user is None:
                print("Wrong card number or PIN!")
            else:
                while True:
                    print(User_Menu)
                    response = str(input())
                    user = search_in_table(tmp_num, tmp_pin)
                    if response == "1":
                        # print("user balance")
                        print("Balance: ", user[2])
                    elif response == "2":
                        print("Adding income")
                        add_income(user)
                    elif response == "3":
                        print("Doing transfer")
                        do_transfer(user)
                    elif response == "4":
                        print("Closing Account")
                        close_acc(user)
                        break
                    elif response == "5":
                        print("You have successfully logged out!")
                        break
                    elif response == "0":
                        print('Bye !')
                        exit(0)
                    connection.commit()

        elif response == "0":
            break
        else:
            continue

    # for obj in BankAcc.acc_obj:
    #     print(obj)
    print("Bye !")
    connection.commit()
    connection.close()
    exit(0)


# #########################Don't use this  Code: for storing data inside the class itself instead of database###########

# class BankAcc:
#     acc_list = dict()
#     acc_obj = []
#
#     def __init__(self):
#         self.number = luhn_num()
#         self.pin = gen_pin()
#         self.Balance = 0
#         BankAcc.acc_list[self.number] = self.pin
#         BankAcc.acc_obj.append(self)
#
#     def get_balance(self):
#         return f"Balance: {self.Balance}"
#
#     def __str__(self):
#         return f'Your card has been created'
#
#
# def log_in():
#     tmp_num = str(input("Enter your card number:"))
#     tmp_pin = str(input("Enter your PIN:"))
#     if tmp_num in BankAcc.acc_list.keys() and tmp_pin in BankAcc.acc_list.values():
#         print("You have successfully logged in!")
#         while True:
#             print("""
#             1. Balance
#             2. Log out
#             0. Exit
#             """)
#             response = str(input())
#             if response == "1":
#                 for obj in BankAcc.acc_obj:
#                     if getattr(obj, 'number') == tmp_num and getattr(obj, 'pin') == tmp_pin:
#                         print(obj.get_balance())
#             elif response == "2":
#                 print("You have successfully logged out!")
#                 return
#             elif response == "0":
#                 exit(0)
#     else:
#         print("Wrong card number or PIN!")

###########################################end of code which use class instead of database to store#####################

# program starts from here and can be used as a module
if __name__ == "__main__":
    main()
