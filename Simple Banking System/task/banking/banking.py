import random
import sqlite3


conn = sqlite3.connect("card.s3db")
cur = conn.cursor()

# cur.execute("""DROP TABLE IF EXISTS card;""")

cur.execute("""CREATE TABLE IF NOT EXISTS card (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0);
""")


try:
    cur.execute("""SELECT number, pin, balance FROM card;""")
    existing_card_nums = {number: {"pin": pin, "balance": balance} for number, pin, balance in cur.fetchall()}

except:
    existing_card_nums = {}


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
        # Otherwise, add it to the dictionary of existing card numbers.
        if card_num in existing_card_nums:
            continue
        else:
            card_pin = random.randint(0, 9999)
            existing_card_nums[card_num] = {"pin": card_pin, "balance": 0}
            cur.execute("""INSERT INTO card (number, pin) VALUES (?,?)""", (card_num, card_pin))
            conn.commit()
            return card_num, card_pin


def log_in(card_num, card_pin):

    try:
        if existing_card_nums[card_num]["pin"] == card_pin:
            return card_num
    except KeyError:
        return None


def get_account_balance(account):

    return existing_card_nums[account]["balance"]


def deposit_money(account, amount):

    existing_card_nums[account]["balance"] = existing_card_nums[account].get("balance", 0) + amount
    new_balance = existing_card_nums[account]["balance"]
    cur.execute("""UPDATE card SET balance = ? WHERE number = ?;""", (new_balance, account))
    conn.commit()
    return "Income was added!"


def transfer_money(from_account, to_account, amount):
    from_account_balance = get_account_balance(from_account)
    to_account_balance = get_account_balance(to_account)
    from_account_balance -= amount
    existing_card_nums[from_account]["balance"] = from_account_balance
    cur.execute("""UPDATE card SET balance = ? WHERE number = ?;""", (from_account_balance, from_account))
    conn.commit()
    to_account_balance += amount
    existing_card_nums[to_account]["balance"] = to_account_balance
    cur.execute("""UPDATE card SET balance = ? WHERE number = ?;""", (to_account_balance, to_account))
    conn.commit()
    return "Success!"


def delete_account(account):

    try:
        del existing_card_nums[account]
        cur.execute("""DELETE FROM card WHERE number = ?""", (account, ))
        conn.commit()
        return "The account has been closed!"
    except KeyError:
        return None


while True:
    user_choice = input("1. Create an account\n2. Log into account\n0. Exit\n")
    if user_choice == "1":
        account_num, pin = create_account()
        print("\nYour card has been created")
        print("Your card number:\n{}\nYour card PIN:\n{}\n".format(account_num, "%04d" % pin))
    elif user_choice == "2":
        account_num = int(input("\nEnter your card number:\n"))
        pin = int(input("Enter your PIN:\n"))
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
                    transfer_account = int(input("Enter card number:\n"))
                    if active_account == transfer_account:
                        print("You can't transfer to the same account!")
                        continue
                    last_digit = str(transfer_account)[-1]
                    if get_checksum(transfer_account) != last_digit:
                        print("Such a card does not exist. Probably you made mistake in the card number. Please try again!")
                        continue
                    if transfer_account not in existing_card_nums:
                        print("Such a card does not exist. Probably you made mistake in the card number. Please try again!")
                        continue
                    transfer_amount = int(input("Enter how much money you want to transfer: "))
                    if active_account_balance < transfer_amount:
                        print("Not enough money!")
                        continue
                    print(transfer_money(active_account, transfer_account, transfer_amount))
                elif logged_in_option == "4":
                    print(delete_account(active_account))
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
