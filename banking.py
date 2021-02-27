import random
import sqlite3


conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card (
id INTEGER,
number TEXT UNIQUE NOT NULL,
pin TEXT NOT NULL,
balance INTEGER DEFAULT 0);
""")


def get_checksum(str_15_digits: str) -> int:
    list_of_nums = [int(digit) for digit in str_15_digits]
    # Implement Luhn Algorithm to generate the checksum.
    # 1. Multiply odd digits by 2.
    odd_digits_doubled = []
    for index, digit in enumerate(list_of_nums):
        if index % 2 == 0:
            odd_digits_doubled.append(digit * 2)
        else:
            odd_digits_doubled.append(digit)
    # 2. Subtract 9 from numbers > 9.
    nine_subtracted = []
    for digit in odd_digits_doubled:
        if digit > 9:
            nine_subtracted.append(digit - 9)
        else:
            nine_subtracted.append(digit)
    # 3. Add all numbers.
    total = sum(nine_subtracted)
    # 4. Generate the checksum so that the sum of all digits is divisible by 10.
    if total % 10 == 0:
        checksum = 0
    else:
        units_digit = int(str(total)[-1])
        checksum = 10 - units_digit
    return checksum


def check_luhn_algorithm(card_num: str) -> bool:
    last_digit = int(card_num[-1])
    if get_checksum(card_num[:-1]) == last_digit:
        return True
    else:
        return False


def create_account() -> tuple:
    while True:
        issuer_id = 400000
        customer_id = random.randint(0, 999999999)
        # Ensure the account number is formatted to 9 digits.
        if customer_id < 100000000:
            customer_id = "%09d" % customer_id
        issuer_and_customer_ids = str(issuer_id) + str(customer_id)
        card_num = issuer_and_customer_ids + str(get_checksum(issuer_and_customer_ids))
        # If the card number is not unique, generate a new card number.
        # Otherwise, add it to the database of existing card numbers.
        cur.execute("""SELECT number FROM card;""")
        existing_card_nums = cur.fetchall()
        if card_num in existing_card_nums:
            continue
        else:
            card_pin = str("%04d" % random.randint(0, 9999))
            cur.execute("""INSERT INTO card (number, pin) VALUES (?,?);""", (card_num, card_pin))
            conn.commit()
            return card_num, card_pin


def log_in(card_num: str, card_pin: str):
    cur.execute("""SELECT number FROM card WHERE number = ? AND pin = ?;""", (card_num, card_pin))
    active_card = cur.fetchone()
    if active_card is None:
        return None
    else:
        return active_card


def get_account_balance(account: str) -> int:
    cur.execute("""SELECT balance FROM card WHERE number = ?;""", (account, ))
    return cur.fetchone()[0]


def deposit_money(account: str, amount: int):
    balance_after_deposit = get_account_balance(account) + amount
    cur.execute("""UPDATE card SET balance = ? WHERE number = ?;""", (balance_after_deposit, account))
    conn.commit()
    print("Income was added!")


def transfer_if_valid() -> bool:
    active_account_balance = get_account_balance(active_account)
    if active_account_balance <= 0:
        print("Not enough money!")
        return False
    transfer_account = input("Enter card number:\n")
    if active_account == transfer_account:
        print("You can't transfer to the same account!")
        return False
    if not check_luhn_algorithm(active_account):
        print("Probably you made mistake in the card number. Please try again!")
        return False
    existing_card_nums = []
    for row in cur.execute("""SELECT number FROM card;""").fetchall():
        existing_card_nums.append(row[0])
    if transfer_account not in existing_card_nums:
        print("Such a card does not exist.")
        return False
    transfer_amount = int(input("Enter how much money you want to transfer: "))
    if active_account_balance < transfer_amount:
        print("Not enough money!")
        return False
    transfer_money(active_account, active_account_balance, transfer_account, transfer_amount)
    return True


def transfer_money(from_account: str, active_account_balance: int, to_account: str, amount: int):
    balance_after_withdrawal = active_account_balance - amount
    cur.execute("""UPDATE card SET balance = ? WHERE number = ?;""", (balance_after_withdrawal, from_account))
    conn.commit()
    balance_after_deposit = get_account_balance(to_account) + amount
    cur.execute("""UPDATE card SET balance = ? WHERE number = ?;""", (balance_after_deposit, to_account))
    conn.commit()
    print("Success!")


def delete_account(account: str):
    cur.execute("""DELETE FROM card WHERE number = ?""", (account, ))
    conn.commit()
    print("The account has been closed!")


active_account = None
while True:
    user_choice = input("1. Create an account\n2. Log into account\n0. Exit\n")
    if user_choice == "1":
        account_num, pin = create_account()
        print("\nYour card has been created")
        print(f"Your card number:\n{account_num}\nYour card PIN:\n{pin}\n")
    elif user_choice == "2":
        account_num = input("\nEnter your card number:\n")
        pin = input("\nEnter your PIN:\n")
        active_account = log_in(account_num, pin)
        if active_account is not None:
            active_account = active_account[0]
            print("\nYou have successfully logged in!")
            while active_account is not None:
                print("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")
                logged_in_option = input()
                if logged_in_option == "1":
                    print(get_account_balance(active_account))
                elif logged_in_option == "2":
                    income = int(input("\nEnter income:\n"))
                    deposit_money(active_account, income)
                elif logged_in_option == "3":
                    transfer_if_valid()
                elif logged_in_option == "4":
                    delete_account(active_account)
                    active_account = None
                elif logged_in_option == "5":
                    active_account = None
                    print("You have successfully logged out!")
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
