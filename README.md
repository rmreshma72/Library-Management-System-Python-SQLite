📚 Library Management System

  A beginner-friendly Python + SQLite project for managing books, members, and borrow/return operations.

🚀 Project Overview
  The Library Management System is a console-based Python application designed to help manage:
  Books (Add / Update / Delete / View)
  Members (Registration / Login)
  Borrow and Return of books
  Fine calculation
  Admin and User roles
  It uses SQLite database, Python, and Tabulate for clean table outputs.
⚙️ How to Run the Project
1️⃣ Install Python
Download from: https://www.python.org/downloads/
2️⃣ Install Required Library
Open terminal / command prompt and run:
pip install tabulate
3️⃣ Open the Project Folder
Navigate to the folder where your .py file is saved.
4️⃣ Run the Program
python Library_Management_System.py
5️⃣ First Login (Admin)
Your database will start empty.
To use Admin mode, manually insert an admin record:
INSERT INTO Members(member_name, username, password, contact, email, role, join_date)
VALUES('Admin', 'admin', '12345', '9999999999', 'admin@gmail.com', 'admin', '2025-01-01');

You can run this using DB Browser or Python shell.
👤 User Features
✔ Register & Login
✔ View all books
✔ Search books by:
    1.Title   2.Author  3. Genre
✔ Borrow a book
✔ Return a book with fine calculation
✔ View borrowed books
✔ Update profile
✔ View profile

👑 Admin Features
✔ Add new books
✔ Update book details
✔ Delete book (only if not borrowed)
✔ View all books
✔ View all members
✔ View all borrowed books
✔ View members who borrowed a specific book (not returned yet)

📦 Database Tables
Author, Genre, Books, Members, Borrow

Each table uses foreign keys for linking authors, genres, members, and borrowing details.

🧪 Validations Implemented
✔ Name: alphabets only
✔ Username: must be unique
✔ Contact number: 10 digits (Regex)
✔ Email format validation

✔ Borrow quantity based on availability

✔ Prevent deleting books that are borrowed
