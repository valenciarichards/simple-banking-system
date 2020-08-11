import random
import sqlite3


conn = sqlite3.connect("card.s3db")
cur = conn.cursor()

cur.execute("""DROP TABLE IF EXISTS card;""")

cur.execute("""CREATE TABLE IF NOT EXISTS card (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0);
""")


def get_checksum(num):
    list_of_nums = [int(digit) for digit in str(num)]
    # Implement Luhn Algorithm to generate the checksum.
    # 1. Multiply odd digits by 2.
    odd_digits_doubled = []
    for index, digit in enumerate(list_of_nums):
        multiple = 1
        if index % 2 == 0:
            multiple = 2
        odd_digits_doubled.append(digit * multiple)
    # 2. Subtract 9 from numbers > 9.
    nine_subtracted = []
    for digit in odd_digits_doubled:
        subtract = 0
        if digit > 9:
            subtract = 9
        nine_subtracted.append(digit - subtract)
    # 3. Add all numbers.
    total = 0
    for digit in nine_subtracted:
        total += digit
    # 4. Generate the checksum so that the sum of all digits is divisible by 10.
    if total % 10 == 0:
        checksum = 0
    else:
        units_digit = int(str(total)[-1])
        checksum = 10 - units_digit
    return checksum


def create_account():
    while True:
        issuer_id = 400000
        customer_id = random.randint(0, 999999999)
        # Ensure the account number is formatted to 9 digits.
        if customer_id < 100000000:
            customer_id = "%09d" % customer_id
        issuer_and_customer_ids = str(issuer_id) + str(customer_id)
        card_num = int(str(issuer_id) + str(customer_id) + str(get_checksum(int(issuer_and_customer_ids))))
        # If the card number is not unique, generate a new card number.
        # Otherwise, add it to the database of existing card numbers.
        cur.execute("""SELECT number FROM card;""")
        existing_card_nums = cur.fetchall()
        if card_num in existing_card_nums:
            continue
        else:
            card_pin = random.randint(0, 9999)
            cur.execute("""INSERT INTO card (number, pin) VALUES (?,?);""", (card_num, card_pin))
            conn.commit()
            return card_num, card_pin


def log_in(card_num, card_pin):
    cur.execute("""SELECT number, pin FROM card WHERE number = ? AND pin = ?;""", (card_num, card_pin))
    if cur.fetchone() is None:
        return None
    else:
        return card_num


def get_account_balance(account):
    cur.execute("""SELECT balance FROM card WHERE number = ?""", (account,))
    account_balance = int(cur.fetchone()[0])
    return account_balance


def deposit_money(account, amount):
    cur.execute("""UPDATE card SET balance = balance + ? WHERE number = ?;""", (amount, account))
    conn.commit()
    return "Income was added!"


def transfer_money(from_account, to_account, amount):
    cur.execute("""UPDATE card SET balance = balance - ? WHERE number = ?;""", (amount, from_account))
    conn.commit()
    cur.execute("""UPDATE card SET balance = balance + ? WHERE number = ?;""", (amount, to_account))
    conn.commit()
    return "Success!"


def delete_account(account):
    cur.execute("""DELETE FROM card WHERE number = ?""", (account, ))
    conn.commit()
    return "The account has been closed!"


active_account = None
while True:
    user_choice = input("1. Create an account\n2. Log into account\n0. Exit\n")
    if user_choice == "1":
        account_num, pin = create_account()
        print("\nYour card has been created")
        print("Your card number:\n{}\nYour card PIN:\n{}\n".format(account_num, "%04d" % pin))
    elif user_choice == "2":
        account_num = input("\nEnter your card number:\n")
        pin = input("Enter your PIN:\n")
        active_account = log_in(account_num, pin)
        if active_account:
            print("\nYou have successfully logged in!")
            while active_account:
                print("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")
                logged_in_option = input()
                if logged_in_option == "1":
                    print(get_account_balance(active_account))
                elif logged_in_option == "2":
                    income = int(input("\nEnter income:\n"))
                    print(deposit_money(active_account, income))
                elif logged_in_option == "3":
                    active_account_balance = get_account_balance(active_account)
                    if active_account_balance <= 0:
                        print("Not enough money!")
                    transfer_account = input("Enter card number:\n")
                    if active_account == transfer_account:
                        print("You can't transfer to the same account!")
                        continue
                    last_digit = int(transfer_account[-1])
                    if get_checksum(transfer_account) != last_digit:
                        print("Probably you made mistake in the card number. Please try again!")
                        continue
                    cur.execute("""SELECT number FROM card;""")
                    if transfer_account not in cur.fetchall():
                        print("Such a card does not exist.")
                        continue
                    transfer_amount = int(input("Enter how much money you want to transfer: "))
                    if active_account_balance < transfer_amount:
                        print("Not enough money!")
                        continue
                    print(transfer_money(active_account, transfer_account, transfer_amount))
                elif logged_in_option == "4":
                    print(delete_account(active_account))
                    active_account = None
                    break
                elif logged_in_option == "5":
                    active_account = None
                    print("You have successfully logged out!")
                    break
                elif logged_in_option == "0":
                    active_account = None
                    conn.close()
                    print("Bye!")
                    quit()
                else:
                    continue
        else:
            print("Wrong card number or PIN!")
    elif user_choice == "0":
        print("Bye!")
        break

conn.close()
