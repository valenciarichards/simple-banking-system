import random


def create_account():
    while True:
        issuer_id_string = "400000"
        customer_acct_num = random.randint(1, 999999999)
        # Check whether the account number has less than 9 digits.
        if customer_acct_num < 100000000:
            customer_acct_num = "%09d" % customer_acct_num
        customer_acct_string = str(customer_acct_num)
        checksum = str(random.randint(0, 9))
        card_num = issuer_id_string + customer_acct_string + checksum
        # If the card number is not unique, generate a new card number.
        # Otherwise, add it to the dictionary of existing card numbers.
        if card_num in existing_card_nums:
            continue
        else:
            card_pin = str(random.randint(1000, 9999))
            existing_card_nums[card_num] = card_pin
            print("\nYour card has been created")
            print("Your card number:\n{}\nYour card PIN:\n{}\n".format(card_num, card_pin))
            return card_num, card_pin


def log_in(card_num, card_pin):
    try:
        if existing_card_nums[card_num] == card_pin:
            return card_num
    except KeyError:
        return None


existing_card_nums = {}
while True:
    print("1. Create an account\n2. Log into account\n0. Exit")
    user_choice = input()
    if user_choice == "1":
        create_account()
    elif user_choice == "2":
        account_num = input("\nEnter your card number:\n")
        pin = input("Enter your PIN:\n")
        active_account = log_in(account_num, pin)
        if active_account is None:
            print("Wrong card number or PIN!\n")
            continue
        else:
            print("\nYou have successfully logged in!\n")
            logged_in_option = input("1. Balance\n2. Log out\n0. Exit\n")
            if logged_in_option == "1":
                print("Balance: 0")
            elif logged_in_option == "2":
                active_account = None
                print("You have successfully logged out!")
            elif logged_in_option == "0":
                quit()
    elif user_choice == "0":
        quit()
