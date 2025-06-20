import os
import sys
from abc import ABC, abstractmethod


class Account(ABC):
    def __init__(self, account_no, balance):
        self.balance =""
        self.account_no = account_no
        self._balance = balance
        self.transactions = []

    def deposit(self, amount):
        self.transactions.append(('deposited Amount', amount))
        self._balance += amount
        self.save_transactions()

    @abstractmethod
    def withdraw(self, amount):
        pass

    def balance_enquiry(self):

        return self.balance()

    def save_transactions(self):
        folder_name = "transaction_history"
        os.makedirs(folder_name, exist_ok=True)

        filename = os.path.join(folder_name, f"{self.account_no}.txt")
        with open(filename, 'w') as file:
            for transaction in self.transactions:
                file.write(f"{transaction[0]}: {transaction[1]}\n")


class CheckingAccount(Account):
    def __init__(self, account_no, balance, credit_limit, overdraft_fee,cnic=""):

        super().__init__(account_no, balance)
        self._credit_limit = credit_limit
        self._overdraft_fee = overdraft_fee
        self.cnic=cnic
    def total_balance(self):
        return self.balance_enquiry() + self._credit_limit

    def withdraw(self, amount):
        if self._balance >= amount:
            self._balance -= amount
            self.transactions.append(('Withdrawal Amount', amount))
            self.save_transactions()
        elif self.total_balance() >= amount:
            self._balance -= amount
            self._credit_limit -= (amount - self.balance_enquiry())
            self._balance -= self._overdraft_fee
            self.transactions.append(('Withdrawal Amount', amount))
            self.save_transactions()
        else:
            raise ValueError("Insufficient Balance, withdrawal not possible!")

    def overdraft_facility(self):
        return self._credit_limit


class SavingAccount(Account):
    def __init__(self, account_no, balance, interest_rate):
        super().__init__(account_no, balance)
        self._interest_rate = interest_rate

    def monthly_interest(self):
        interest_amount = self._balance * self._interest_rate
        self._balance += interest_amount
        self.transactions.append(('Monthly Interest:', interest_amount))
        self.save_transactions()

    def withdraw(self, amount):
        if self._balance >= amount:
            self._balance -= amount
            self.transactions.append(('Withdrawal Amount:', amount))
            self.save_transactions()
        else:
            raise ValueError("Insufficient balance. Withdrawal not possible.")

    def __str__(self):
        return f"Account Number: {self.account_no}, Balance: {self._balance}"


class LoanAccount(Account):
    def __init__(self, account_no, balance, interest_rate, loan_duration, principal_amount):
        super().__init__(account_no, balance)
        self.interest_rate = interest_rate
        self.loan_duration = loan_duration
        self.principal_amount = principal_amount

    def monthly_payment(self):
        monthly_interest = self._balance * self.interest_rate
        total_payment = monthly_interest + (self.principal_amount / self.loan_duration)
        self._balance -= total_payment
        self.transactions.append(('Monthly Payment:', total_payment))
        self.save_transactions()

    def withdraw(self, amount):
        self.transactions.append(('Withdrawal Amount', amount))
        self.save_transactions()
        raise ValueError("Withdrawal is not allowed for Loan Account.")

    def __str__(self):
        return f"Account Number: {self.account_no}, Balance: {self._balance}"


class LoanCheck:
    def __init__(self, account_no='', loan_amount=0, loan_duration=0, interest_rate=0):
        self.account_no = account_no
        self.loan_amount = loan_amount
        self.loan_duration = loan_duration
        self.interest_rate = interest_rate

    def check_loan_status(self):
        print(f"Account Number: {self.account_no}")
        print(f"Loan Amount: {self.loan_amount}")
        print(f"Loan Duration: {self.loan_duration} months")
        print(f"Interest Rate: {self.interest_rate}%")


class Customer:
    def __init__(self, username='', password='', first_name='', last_name='', address='', cnic=''):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.cnic = cnic
        self.accounts = []
        #self.load_customer_data()
        #self.load_account_data()

    def load_account_data(self):
        folder_name = "customer_data"
        os.makedirs(folder_name, exist_ok=True)

        filename = os.path.join(folder_name, f"{self.cnic}.txt")
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                lines = file.readlines()
                i = 0
                while i < len(lines):
                    if lines[i].startswith("Account Number:"):
                        account_no = lines[i].split(":")[1].strip()
                        account_type = lines[i + 1].split(":")[1].strip()
                        balance = float(lines[i + 2].split(":")[1].strip())
                        if account_type == "CheckingAccount":
                            credit_limit = float(lines[i + 3].split(":")[1].strip())
                            overdraft_fee = float(lines[i + 4].split(":")[1].strip())
                            account = CheckingAccount(account_no, balance, credit_limit, overdraft_fee)
                            i += 5
                        elif account_type == "SavingAccount":
                            interest_rate = float(lines[i + 3].split(":")[1].strip())
                            account = SavingAccount(account_no, balance, interest_rate)
                            i += 4
                        elif account_type == "LoanAccount":
                            interest_rate = float(lines[i + 3].split(":")[1].strip())
                            loan_duration = int(lines[i + 4].split(":")[1].strip())
                            principal_amount = float(lines[i + 5].split(":")[1].strip())
                            account = LoanAccount(account_no, balance, interest_rate, loan_duration, principal_amount)
                            i += 6
                        else:
                            raise ValueError(f"Invalid account type: {account_type}")
                        self.accounts.append(account)
                    else:
                        i += 1

    def find_account(self, account_no):
        for account in self.accounts:
            if account.account_no == account_no:
                return account
        return None

    def print_account_details(self, account_no):
        account = self.find_account(account_no)
        if account is not None:
            folder_name = "account_data"
            filename = os.path.join(folder_name, f"{account.account_no}.txt")
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    print(file.read())
            else:
                print("Account file not found.\n")
        else:
            print("Account not found.\n")


    def main(self):
        # Ask for user details
        print("\nPlease provide your details:")
        self.username = input("Username: ")
        self.password = input("Password: ")
        self.first_name = input("First Name: ")
        self.last_name = input("Last Name: ")
        self.address = input("Address: ")
        self.cnic = input("CNIC: ")
#        self.load_customer_data()

        # Append customer details to a file
        self.append_to_file()

    def append_to_file(self):
        folder_name = "customer_data"
        os.makedirs(folder_name, exist_ok=True)

        filename = os.path.join(folder_name, f"{self.cnic}.txt")  # Filename based on CNIC
        with open(filename, 'a') as file:
            file.write(f"Username: {self.username}\n")
            file.write(f"Password: {self.password}\n")
            file.write(f"First Name: {self.first_name}\n")
            file.write(f"Last Name: {self.last_name}\n")
            file.write(f"Address: {self.address}\n")
            file.write(f"CNIC: {self.cnic}\n")
            file.write("-----\n")
        print(f"Data appended to the file '{filename}' successfully.")

    def save_account_data(self):
        folder_name = "customer_data"
        os.makedirs(folder_name, exist_ok=True)

        filename = os.path.join(folder_name, f"{self.cnic}.txt")
        with open(filename, 'w') as file:
            for account in self.accounts:
                if isinstance(account, CheckingAccount):
                    account_type = "CheckingAccount"
                    file.write(f"Account Number: {account.account_no}\n")
                    file.write(f"Account Type: {account_type}\n")
                    file.write(f"Balance: {account.balance_enquiry()}\n")
                    file.write(f"Credit Limit: {account.overdraft_facility()}\n")
                    file.write(f"Overdraft Fee: {account._overdraft_fee}\n")
                elif isinstance(account, SavingAccount):
                    account_type = "SavingAccount"
                    file.write(f"Account Number: {account.account_no}\n")
                    file.write(f"Account Type: {account_type}\n")
                    file.write(f"Balance: {account.balance_enquiry()}\n")
                    file.write(f"Interest Rate: {account._interest_rate}\n")
                elif isinstance(account, LoanAccount):
                    account_type = "LoanAccount"
                    file.write(f"Account Number: {account.account_no}\n")
                    file.write(f"Account Type: {account_type}\n")
                    file.write(f"Balance: {account.balance_enquiry()}\n")
                    file.write(f"Interest Rate: {account.interest_rate}\n")
                    file.write(f"Loan Duration: {account.loan_duration}\n")
                    file.write(f"Principal Amount: {account.principal_amount}\n")
                file.write("-----\n")

    def create_account(self):
        account_type = input("Enter account type (1 - Checking, 2 - Saving, 3 - Loan): ")
        if account_type == '1':
            self.main()
            account_no = input("Enter account number: ")
            balance = float(input("Enter initial balance: "))
            credit_limit = float(input("Enter credit limit: "))
            overdraft_fee = float(input("Enter overdraft fee: "))
            account = CheckingAccount(account_no, balance, credit_limit, overdraft_fee, self.cnic)
            self.accounts.append(account)
            print("Checking Account created successfully!\n")
        elif account_type == '2':
            self.main()
            account_no = input("Enter account number: ")
            balance = float(input("Enter initial balance: "))
            interest_rate = float(input("Enter interest rate: "))
            account = SavingAccount(account_no, balance, interest_rate)
            self.accounts.append(account)
            print("Saving Account created successfully!\n")
        elif account_type == '3':
            self.main()
            account_no = input("Enter account number: ")
            balance = float(input("Enter initial balance: "))
            interest_rate = float(input("Enter interest rate: "))
            loan_duration = int(input("Enter loan duration in months: "))
            principal_amount = float(input("Enter principal loan amount: "))
            account = LoanAccount(account_no, balance, interest_rate, loan_duration, principal_amount)
            self.accounts.append(account)
            print("Loan Account created successfully!\n")
        else:
            print("Invalid account type.\n")

    def find_account(self, account_no):
        for account in self.accounts:
            if account.account_no == account_no:
                return account
        return None

    def loan_inquiry(self):
        account_no = input("Enter account number: ")
        account = self.find_account(account_no)
        if account is not None and isinstance(account, LoanAccount):
            loan = LoanCheck(account_no, account.balance_enquiry(), account.loan_duration, account.interest_rate)
            loan.check_loan_status()
        else:
            print("Loan account not found.\n")

    def info(self):
        print('\n___WELCOME TO SMA BANK___\n')

        # Load account data from files
        self.load_account_data()

        while True:
            print("1. Create Account")
            print("2. Deposit")
            print("3. Withdraw")
            print("4. Balance Enquiry")
            print("5. Loan Inquiry")
            print("6. Exit\n")
            print("7. BACK")
            choice = input("Enter your choice: ")

            if choice == '1':
                self.create_account()
                self.save_account_data()
                self.load_account_data()
            elif choice == '2':
                account_no = input("Enter account number: ")
                amount = float(input("Enter amount to deposit: "))
                account = self.find_account(account_no)
                if account is not None:
                    account.deposit(amount)
                    self.save_account_data()
                    print("Deposit successful!\n")
                else:
                    print("Account not found.\n")

            elif choice == '3':
                account_no = input("Enter account number: ")
                amount = float(input("Enter amount to withdraw: "))
                account = self.find_account(account_no)
                if account is not None:
                    try:
                        account.withdraw(amount)
                        self.save_account_data()

                        print("Withdrawal successful!\n")
                    except ValueError as e:
                        print(str(e))
                else:
                    print("Account not found.\n")

            elif choice == '4':
                account_no = input("Enter account number: ")
                account = self.find_account(account_no)
                if account is not None:
                    balance = account.balance_enquiry()
                    print(f"Account Balance: {balance}")
                else:
                    print("Account not found.")

            elif choice == '5':
                self.loan_inquiry()

            elif choice == '6':
                print("Thank you for using our banking services!\n")
                break
            elif choice =="7":
                return login()

            else:
                print("Invalid choice. Please try again.\n")


class BankAdmin:
    def __init__(self, bank_employee_name='', contact_number=''):
        self.bank_employee_name = bank_employee_name
        self.contact_number = contact_number

    def update_bank_details(self):
        print('\n_______SMA BANK ADMIN INTERFACE_______\n')
        print('Enter Bank Details:')
        self.bank_employee_name = input("Employee Name: ")
        self.contact_number = input("Contact Number: ")
        print()

    def read_customer_data(self):
        folder_name = "customer_data"
        for filename in os.listdir(folder_name):
            with open(os.path.join(folder_name, filename), 'r') as file:
                print(file.read())

    def print_account_info(self, customer):
        print('\n_______ACCOUNT INFORMATION_______\n')
        account_no = input("Enter account number: ")
        account = customer.find_account(account_no)
        if account is not None:
            print(account)
        else:
            print("Account not found.")

    def admin_interface(self, customer):
        print("\n_______ADMIN INTERFACE_______\n")
        while True:
            print("1. Read Customer Data")
            print("2. Print Account Information")
            print("3. Exit\n")

            choice = input("Enter your choice: ")

            if choice == '1':
                self.read_customer_data()

            elif choice == '2':
                self.print_account_info(customer)

            elif choice == '3':
                print("Exiting admin interface.")
                break

            else:
                print("Invalid choice. Please try again.\n")


# Login System
def login():
    print("\n_______WELCOME TO SMA BANK_______\n")
    while True:
        user_type = input("Select user type (1 - Admin, 2 - Customer, 3 - Exit): ")
        if user_type == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            if username == "admin" and password == "password":
                admin = BankAdmin()
                admin.update_bank_details()
                customer = Customer()
                admin.admin_interface(customer)
                break
            else:
                print("Invalid username or password. Please try again.\n")
        elif user_type == '2':
            customer = Customer()
            customer.load_account_data()
            customer.info()
            break
        elif user_type == '3':
            break
        else:
            print("Invalid user type. Please try again.\n")


# Test Code
login()
