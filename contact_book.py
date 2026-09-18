"""
Contact Book Application
A console-based contact management system that lets users add, view,
search, update, and delete contacts. Contacts are stored persistently
in a JSON file so they remain available between sessions.

Internship: CodSoft
"""

import json
import os

DATA_FILE = "contacts.json"


def load_contacts():
    """Load contacts from the JSON file, or return an empty dict."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_contacts(contacts):
    """Save contacts to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(contacts, f, indent=4)


def add_contact(contacts):
    print("\n--- Add New Contact ---")
    name = input("Name: ").strip()
    if name in contacts:
        print(f"A contact named '{name}' already exists. Use Update instead.")
        return

    phone = input("Phone Number: ").strip()
    email = input("Email: ").strip()
    address = input("Address: ").strip()

    contacts[name] = {
        "phone": phone,
        "email": email,
        "address": address
    }
    save_contacts(contacts)
    print(f"Contact '{name}' added successfully.")


def view_contacts(contacts):
    print("\n--- Contact List ---")
    if not contacts:
        print("No contacts saved yet.")
        return

    print(f"{'Name':<20}{'Phone':<15}")
    print("-" * 35)
    for name, details in contacts.items():
        print(f"{name:<20}{details.get('phone', ''):<15}")


def search_contact(contacts):
    print("\n--- Search Contact ---")
    query = input("Enter name or phone number to search: ").strip().lower()

    results = {
        name: details
        for name, details in contacts.items()
        if query in name.lower() or query in details.get("phone", "").lower()
    }

    if not results:
        print("No matching contacts found.")
        return

    print(f"\nFound {len(results)} matching contact(s):")
    for name, details in results.items():
        print_contact(name, details)


def print_contact(name, details):
    print("-" * 30)
    print(f"Name:    {name}")
    print(f"Phone:   {details.get('phone', '')}")
    print(f"Email:   {details.get('email', '')}")
    print(f"Address: {details.get('address', '')}")


def update_contact(contacts):
    print("\n--- Update Contact ---")
    name = input("Enter the name of the contact to update: ").strip()

    if name not in contacts:
        print(f"No contact named '{name}' found.")
        return

    print("Leave a field blank to keep it unchanged.")
    details = contacts[name]

    new_phone = input(f"Phone [{details.get('phone', '')}]: ").strip()
    new_email = input(f"Email [{details.get('email', '')}]: ").strip()
    new_address = input(f"Address [{details.get('address', '')}]: ").strip()

    if new_phone:
        details["phone"] = new_phone
    if new_email:
        details["email"] = new_email
    if new_address:
        details["address"] = new_address

    save_contacts(contacts)
    print(f"Contact '{name}' updated successfully.")


def delete_contact(contacts):
    print("\n--- Delete Contact ---")
    name = input("Enter the name of the contact to delete: ").strip()

    if name not in contacts:
        print(f"No contact named '{name}' found.")
        return

    confirm = input(f"Are you sure you want to delete '{name}'? (y/n): ").strip().lower()
    if confirm == "y":
        del contacts[name]
        save_contacts(contacts)
        print(f"Contact '{name}' deleted successfully.")
    else:
        print("Deletion cancelled.")


def print_menu():
    print("\n===== Contact Book =====")
    print("1. Add Contact")
    print("2. View Contact List")
    print("3. Search Contact")
    print("4. Update Contact")
    print("5. Delete Contact")
    print("6. Exit")


def main():
    contacts = load_contacts()

    while True:
        print_menu()
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            add_contact(contacts)
        elif choice == "2":
            view_contacts(contacts)
        elif choice == "3":
            search_contact(contacts)
        elif choice == "4":
            update_contact(contacts)
        elif choice == "5":
            delete_contact(contacts)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose a number between 1 and 6.")


if __name__ == "__main__":
    main()