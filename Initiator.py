import subprocess

def main():
    print("Welcome! Please select the script you want to run:")
    print("1. Refresh balance")
    print("2. Start refuel")
    print("3. Start Testnet swap")
    print("4. Start minting some random shit")

    choice = input("Enter your choice: ")

    if choice == "1":
        subprocess.run(['python', 'Get_all_value.py'])
    elif choice == "2":
        subprocess.run(['python', 'Refuel.py'])
    elif choice == "3":
        subprocess.run(['python', 'Testnet_swap.py'])
    elif choice == "4":
        subprocess.run(['python', 'ZK_nft_mint.py'])
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
