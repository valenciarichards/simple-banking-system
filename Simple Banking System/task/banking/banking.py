import random


def create_account():
    while True:
        issuer_id = 400000
        customer_id = random.randint(0, 999999999)
        # Ensure the account number is formatted to 9 digits.
        if customer_id < 100000000:
            customer_id = "%09d" % customer_id
        issuer_and_customer_ids = str(issuer_id) + str(customer_id)
        issuer_and_customer_ids_list = [int(digit) for digit in issuer_and_customer_ids]
        # Implement Luhn Algorithm to generate the checksum.
        # 1. Multiply odd digits by 2.
        odd_digits_doubled = []
        for index, digit in enumerate(issuer_and_customer_ids_list):
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
        # print("total = {}, checksum = {}".format(total, checksum))
        card_num = int(str(issuer_id) + str(customer_id) + str(checksum))
        # If the card number is not unique, generate a new card number.
        # Otherwise, add it to the dictionary of existing card numbers.
        if card_num in existing_card_nums:
            continue
        else:
            card_pin = random.randint(0, 9999)
            existing_card_nums[card_num] = card_pin
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
        account_num, pin = create_account()
        print("\nYour card has been created")
        print("Your card number:\n{}\nYour card PIN:\n{}\n".format(account_num, "%04d" % pin))
    elif user_choice == "2":
        account_num = int(input("\nEnter your card number:\n"))
        pin = int(input("Enter your PIN:\n"))
        active_account = log_in(account_num, pin)
        if active_account is not None:
            print("\nYou have successfully logged in!\n")
            logged_in_option = input("1. Balance\n2. Log out\n0. Exit\n")
            if logged_in_option == "1":
                print("Balance: 0")
            elif logged_in_option == "2":
                active_account = None
                print("You have successfully logged out!")
            elif logged_in_option == "0":
                quit()
        else:
            print("Wrong card number or PIN!")
    elif user_choice == "0":
        quit()
