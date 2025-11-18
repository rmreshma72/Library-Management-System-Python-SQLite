import sys
import sqlite3
import datetime
import re
from tabulate import tabulate 
from getpass import getpass

conn = sqlite3.connect('Library.db')
cursor = conn.cursor()
#..........................................TABLES......................................................#

cursor.execute('''
CREATE TABLE IF NOT EXISTS Author(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               author_name VARCHAR(20))
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Genre(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               genre_name VARCHAR(20) )
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Books(
               book_id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               total_copies INTEGER,
               available_copies INTEGER,
               is_Available INTEGER DEFAULT 1,
               author_id INTEGER,
               genre_id INTEGER,
               FOREIGN KEY (author_id) REFERENCES Author(id),
               FOREIGN KEY (genre_id) REFERENCES Genre(id))
 ''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS Members(
               member_id INTEGER PRIMARY KEY AUTOINCREMENT,
               member_name VARCHAR(20) NOT NULL,
               username VARCHAR(20) NOT NULL UNIQUE,
               password TEXT NOT NULL,
               contact TEXT NOT NULL,
               email VARCHAR(20),
               role TEXT DEFAULT 'user',
               join_date DATE)

''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS Borrow(
               borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
               book_id INTEGER,
               member_id INTEGER,
               borrow_date DATE,
               due_date DATE,
               return_date DATE DEFAULT NULL,
               fine REAL DEFAULT 0,
               FOREIGN KEY (book_id) REFERENCES Books(book_id),
               FOREIGN KEY (member_id) REFERENCES Members(member_id))
''')

#..........................TRY....EXCEPT............................#

# For invalid choice
def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("❌ Please enter a valid number!")

# For invalid book or borrow id
def get_id(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("❌ Please enter a valid ID!")

#.............................CHECK....................................#
def check_name(name):
    result  = True if re.fullmatch(r'^[A-Za-z ]+$',name) else False
    return result

def check_contact(contact):
    result = True if re.fullmatch(r'\d{10}',contact) else False
    return result

def check_email(email):
    result = True if re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$',email) else False
    return result

#...........................VIEW BOOKS..........................#
def viewBooks(role , member_id = 1):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    print('================= ALL BOOKS  =================\n')
    cursor.execute('''
    SELECT
                   Books.book_id,
                   Books.title,
                   Books.total_copies,
                   Books.available_copies,
                   Author.author_name,
                   Genre.genre_name
    FROM Books
    JOIN Author ON Books.author_id = Author.id
    JOIN Genre ON Books.genre_id = Genre.id''')
    allbooks = cursor.fetchall()
    if not allbooks:
        print ('Books not available..🙁')
    if role == 'admin':
        headers = [desc[0] for desc in cursor.description]
        print(tabulate(allbooks,headers,tablefmt='fancy_grid'))
    elif role == 'user' :
        headers = [desc[0] for desc in cursor.description]
        selected_columns = ['book_id','title','available_copies','author_name','genre_name']
        indexes = [headers.index(col) for col in selected_columns]
        filtered_rows = [[row[i] for i in indexes] for row in allbooks]
        print(tabulate(filtered_rows, headers = selected_columns, tablefmt = 'fancy_grid'))
        borrow_option = input('Do you want to borrow a book ?(Y/N) : ' ).lower()
        if borrow_option == 'y':
            book_id = int(input('Enter book_id you want to borrow : '))
            borrow_a_book(member_id,book_id)

        

    conn.close()

#...........................VIEW PROFILE........................#
def viewProfile(member_id):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()

    print ( '\n ================= PROFILE =================\n')
    
    cursor.execute('''SELECT * FROM Members WHERE member_id = ?''',(member_id,))
    member = cursor.fetchone()
    headers =[desc[0] for desc in cursor.description]
    print(tabulate([member], headers, tablefmt='fancy_grid'))
    conn.close()

#...........................UPDATE PROFILE......................#
def update_profile(member_id):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    while True:
        print('\n================= UPDATE PROFILE =================\n')
        print('1.Change Name')
        print('2.Change password')
        print('3.Change Contact')
        print('4.Change email')
        print('5.Go Back')
        ch = get_int('\nEnter your choice : ')
        if ch == 1:
            while True:
                new_name = input('Enter new name : ').strip()
                if check_name(new_name):break
                else: print("❌ Name can contain only letters and spaces.")
            
            cursor.execute('''UPDATE Members SET member_name = ? WHERE member_id = ?''',(new_name,member_id))
            conn.commit()
            print('\n 👍 Name updated Successfully...✅')

        elif ch == 2:
            old_password =input('Enter current password :')
            cursor.execute(''' SELECT password FROM Members WHERE member_id =? AND password = ?''',(member_id,old_password))
            old_pass = cursor.fetchone()
            if old_pass and old_pass[0] == old_password :
                new_password = input('Enter new password : ')
                cursor.execute('''UPDATE Members SET password = ? WHERE member_id = ?''',(new_password,member_id))
                conn.commit()
                print('\n🔑 Password updated Successfully...✅')
            else:
                print('Incorrect password..❌')
        
        elif ch == 3:
            while True:
                new_contact = input('Enter new contact number : ')
                if check_contact(new_contact): break
                else:
                    print("⚠ Please enter a valid 10-digit mobile number (numbers only, no spaces).")
            
            cursor.execute('''UPDATE Members SET contact = ? WHERE member_id = ?''',(new_contact,member_id))
            conn.commit()
            print('\n📞 Contact updated Successfully...✅')
        
        elif ch == 4 :
            while True:
                new_email = input('Enter new email : ').strip()
                if check_email(new_email):  break
                else: print("⚠ Invalid email..")
            
            cursor.execute('''UPDATE Members SET email = ? WHERE member_id = ?''',(new_email,member_id))
            conn.commit()
            print('\n📧 Email updated Successfully...✅')
        elif ch == 5:
            break
        else :
            print ('❌ Invalid Choice....') 
    conn.close()  

#...........................BORROWED BOOKS.......................#
def borrowed_books(member_id):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    print('================= 📚 BORROWED BOOKS 📚 =================\n')
    cursor.execute('''
    SELECT 
            Borrow.borrow_id,
            Borrow.book_id,
            Books.title,
            Borrow.borrow_date,
            Borrow.due_date,
            Borrow.return_date,
            Borrow.fine
    FROM Borrow
    JOIN Books ON Borrow.book_id = Books.book_id
    WHERE Borrow.member_id = ? ''',(member_id,))
    
    books = cursor.fetchall()

    if not books:
        print('\n📚 You have not borrowed any books yet.')
    else:
        headers = [desc[0] for desc in cursor.description]
        print(tabulate(books,headers,tablefmt='fancy_grid'))
    
    conn.close()


#...........................RETURN A BOOK........................#
def return_a_book(member_id):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    fine_per_day = 5
    
    borrowed_books(member_id)
    print('\n================= RETURN BOOK📗 =================\n')
    borrow_id = get_id('Enter borrow_id to return : ')
    
    cursor.execute('''
    SELECT borrow_id, book_id, due_date  from Borrow WHERE borrow_id = ? AND member_id = ? AND return_date IS NULL
                   ''',(borrow_id,member_id))

    book = cursor.fetchone()
    if not book:
        print('Invalid borrow_id..' )
        conn.close()
        return
    else:
        borrow_id ,book_id, due_date = book
        return_date = datetime.date.today()
        due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
        difference = (return_date - due_date).days

        fine = fine_per_day *  difference if difference > 0 else 0
            
        cursor.execute('''
        UPDATE Borrow SET return_date = ?, fine = ? WHERE borrow_id = ?
                           ''',(return_date,fine,borrow_id))
            
        cursor.execute('''
        UPDATE Books SET available_copies = available_copies + 1 WHERE book_id = ?
                           ''',(book_id,))
        conn.commit()
        conn.close()
        print ('\n📚 Book returned successfully...')
        if fine > 0:
            print(f' Fine : {fine}')
        else:
            print('No fine.')


#...........................BORROW...............................#
def borrow_a_book(member_id,book_id):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT book_id, title, available_copies FROM Books WHERE book_id = ?
                   ''',(book_id,))
    book = cursor.fetchone()

    if not book:
        print('❌ Book not Found..')
        conn.close()
        return
    
    else:
        book_id , book_title, available = book

        if available == 0:
            print('Book is Out of Stock..')
            conn.close()
            return
        else:
            borrow_date = datetime.date.today()
            due_date = borrow_date + datetime.timedelta(days=14)
            
            cursor.execute('''
            INSERT INTO Borrow (book_id, member_id, borrow_date, due_date) VALUES(?,?,?,?)
                           ''',(book_id,member_id,borrow_date,due_date)) 

            cursor.execute('''
            UPDATE Books SET available_copies = available_copies - 1 WHERE book_id = ?''',(book_id,)) 
            conn.commit()
            conn.close()
            print(f"\n📚 You borrowed: {book_title}")
            print(f"📅 Due Date: {due_date}\n")

#..........................................SEARCH........................................................#
def search_by_book_title(member_id):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    print('\n=================🔎 SEARCH BY BOOK TITLE =================\n')
    title = input('Enter the book_title:')
    cursor.execute(''' SELECT book_id, title, available_copies FROM Books 
                   WHERE title LIKE ?
                   ''',('%' + title + '%',))
    book = cursor.fetchone()
    if book:
        headers = [desc[0] for desc in cursor.description]
        print(tabulate([book], headers, tablefmt = 'fancy_grid'))

        borrow_option = input('Do you want to borrow this book ?(Y/N) : ' ).lower()
        if borrow_option == 'y':
            book_id = get_id('Enter book_id you want to borrow : ')
            borrow_a_book(member_id,book_id)
    else:
        print ("Sorry, the book is not available right now.")
    conn.close()


def search_by_author(member_id):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    print('\n================= 🔎 SEARCH BY AUTHOR NAME =================\n')

    author_name = input('Enter author name:')
    cursor.execute('''
       SELECT Books.book_id, Books.title, Author.author_name, Books.available_copies
        FROM Books
        JOIN Author ON Books.author_id = Author.id
        WHERE Author.author_name LIKE ?
    ''', ('%' + author_name + '%',))

    books = cursor.fetchall()

    if books:
        headers = [desc[0] for desc in cursor.description]
        print(f'\n Books by {author_name} :\n')
        print(tabulate(books, headers, tablefmt='fancy_grid'))

        borrow_option = input('Do you want to borrow this book ?(Y/N) : ' ).lower()
        if borrow_option == 'y':
            book_id = get_id('Enter book_id you want to borrow : ')
            borrow_a_book(member_id,book_id)
    else:
        print('❌ No books found by this author...')

    conn.close()
    

def search_by_genre(member_id):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()

    print('\n================= 🔎 SEARCH BY GENRE =================\n')

    genre = input('Enter genre:')
    cursor.execute('''
       SELECT Books.book_id, Books.title, Genre.genre_name, Books.available_copies
        FROM Books
        JOIN Genre ON Books.genre_id = Genre.id
        WHERE Genre.genre_name LIKE ?
    ''', ('%' + genre + '%',))

    books = cursor.fetchall()

    
    if books:
        
        headers = [desc[0] for desc in cursor.description]
        print(f'\n Books in {genre} Genre :\n')
        print(tabulate(books, headers, tablefmt='fancy_grid'))

        borrow_option = input('Do you want to borrow this book ?(Y/N) : ' ).lower()
        if borrow_option == 'y':
            book_id = get_id('Enter book_id you want to borrow : ')
            borrow_a_book(member_id,book_id)

    else:
        print('❌ No books with this genre...')

    conn.close()
    


#...........................................USER........................................................#
def userMenu(member_id,member_name):
    print('\nWELCOME ', member_name)
    while True:
        try:
            print('\n1.VIEW ALL BOOKS')
            print('2.SEARCH BOOK')
            print('3.Return A BOOK')
            print('4.View BORROWED BOOKS')
            print('5.Update Profile/Password')
            print('6.View Profile')
            print('7.Log Out\n')

            ch = get_int('Enter your choice:')
            if ch == 1:
                viewBooks('user',member_id)
            elif ch == 2:
                print('\nSEARCH BY:\n\n1.Book Title\n2.Author\n3.Genre\n4.Previous Menu')
                s_ch=int(input('\nEnter your choice:'))
                if s_ch == 1:
                    search_by_book_title(member_id)
                elif s_ch == 2:
                    search_by_author(member_id)
                elif s_ch == 3:
                    search_by_genre(member_id)
                elif s_ch == 4:
                    continue
                else:
                    print('invalid choice')
            elif ch == 3:
                return_a_book(member_id)
            elif ch == 4:
                borrowed_books(member_id)
            elif ch == 5:
                update_profile(member_id)
            elif ch == 6:
                viewProfile(member_id)
            elif ch == 7:
                break
                
            else:
                print('Invalid Choice...')

        except ValueError:
            print('Invalid choice')

def register():
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()

    print('\n...............REGISTRATION..............\n')
    while True:
        name = input("Enter your name: ").strip()
        if check_name(name): break
        else:
            print("\n ❌ Name can contain only letters and spaces.")

    #username = Unique
    while(True):
        username = input('Enter Username: ')
        cursor.execute('''SELECT username FROM Members WHERE username = ?''',(username,))
        already_exist = cursor.fetchone()
        if already_exist:
            print('\n❌ Username already exist... Please Try again..')
        else:
            break

    password = input('Enter password: ')

    #Contact validation
    while True:
        contact = input('Enter contact number: ').strip()
        if check_contact(contact):  break
        else:
            print("\n⚠ Please enter a valid 10-digit mobile number (numbers only, no spaces).")
    #Email validation
    while True:
        email =  input('Enter email: ').strip()
        if email == '':
            break
        if check_email(email): break
        else:
            print("\n⚠ Invalid email..")

    join_date = datetime.date.today()

    cursor.execute('''
    INSERT INTO Members(member_name, username, password, contact, email, join_date)
                   VALUES(?,?,?,?,?,?)
''',(name,username,password,contact,email,join_date))
    
    print ('\nRegistration Successfull..✅')
    
    conn.commit()
    conn.close()
    return

    
def loginUser():
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    print('\n================= USER LOGIN  =================\n')

    print('1. NEW HERE? Sign Up\n2. Login\n')
    ch = get_int('Enter the choice:')
    while True:
        try:
            if ch == 1 :
                register()
                break
            elif ch == 2 :
                print('\n................LOGIN..................\n')
                username = input('USERNAME : ')
                password = getpass('PASSWORD : ')
                cursor.execute(''' SELECT member_id, member_name FROM Members WHERE username = ? AND password = ?''',(username,password))
                all_data = cursor.fetchone()
                if all_data :
                    member_id = all_data[0]
                    member_name = all_data[1]
                    userMenu(member_id,member_name)
                    break
                else :
                    print ('Invalid Username or Password ❌ ... Try again..')
        except ValueError:
            print ('Invalid Username or Password ❌ ... Try again..')



#..........................................ADMIN.........................................................#

def viewMembers():
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    print('\n================= ALL MEMBERS =================\n')
    cursor.execute('''SELECT * FROM Members WHERE role = 'user' ''')
    all_members = cursor.fetchall()

    if not all_members:
        print ('No members...')
    else:
        headers = [desc[0] for desc in cursor.description]
        print(tabulate(all_members,headers,tablefmt='fancy_grid'))


def view_members_by_bookID():
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    print("\n=================🔎 SEARCH BORROW RECORD BY BOOK ID=================")
    book_id = get_id('\nEnter the book_id :')

    cursor.execute("SELECT title FROM Books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()

    if not book:
        print("\n❌ Invalid Book ID! No such book found.")
        conn.close()
        return

    book_title = book[0]
    print(f"\n📘 Book: {book_title}")

    cursor.execute('''
        SELECT
                Borrow.borrow_id,
                Members.member_name,
                Members.contact,
                Members.email,
                Books.title,
                Borrow.borrow_date,
                Borrow.due_date
        FROM Borrow
        JOIN Members ON Borrow.member_id = Members.member_id
        JOIN Books ON Borrow.book_id = Books.book_id
        WHERE Books.book_id = ? AND Borrow.return_date IS NULL''',(book_id,))
    
    data = cursor.fetchall()

    if not data:
        print ('\n✔ No pending returns for this book.')
    else:
        headers = [desc[0] for desc in cursor.description]
        print(tabulate( data, headers, tablefmt='fancy_grid'))

    conn.close()


def admin_borrowed_books():
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()

    print('\n================= BORROWED BOOKS =================\n')

    cursor.execute('''
    SELECT
                   Borrow.borrow_id,
                   Members.member_name,
                   Books.title,
                   Borrow.borrow_date,
                   Borrow.due_date,
                   Borrow.return_date,
                   Borrow.fine
                   FROM Borrow
                   JOIN Members ON Borrow.member_id = Members.member_id
                   JOIN Books ON Borrow.book_id = Books.book_id
                   ''')
    data = cursor.fetchall()
    if not data:
        print ('\n No borrowed books found....')
    else:
        headers = [desc[0] for desc in cursor.description]
        print(tabulate(data , headers, tablefmt= 'fancy_grid'))

    conn.close()

def insertAuthor(conn,cursor,author):
    cursor.execute('''
SELECT id FROM Author WHERE author_name = ?''',(author,))
    a_id = cursor.fetchone()
    if a_id:
        return a_id[0]
    
    cursor.execute('''INSERT INTO Author(author_name) VALUES(?)''',(author,))
    conn.commit()
    return cursor.lastrowid


def insertGenre(conn,cursor,genre):
    cursor.execute('''
SELECT id FROM Genre WHERE genre_name = ?''',(genre,))
    g_id = cursor.fetchone()
    if g_id:
        return g_id[0]
    
    cursor.execute('''INSERT INTO Genre(genre_name) VALUES(?)''',(genre,))
    conn.commit()
    return cursor.lastrowid


def insertBooks():
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()

    print('\n================= INSERT BOOK =================\n')
    
    title = input('Enter the Book Title: ')
    author = input('Enter author name: ')
    genre = input('Enter the genre: ')
    copies = get_int('Enter total number of copies: ')

    authorID = insertAuthor(conn,cursor,author)
    genreID = insertGenre(conn,cursor,genre)

    cursor.execute('''
    INSERT INTO Books(title,total_copies,available_copies,author_id,genre_id)
                VALUES(?,?,?,?,?)
''',(title,copies,copies,authorID,genreID))
    
    print('\nBOOK INSERTED SUCCESSFULLY..✅')
    conn.commit()
    conn.close()

def update_book():
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    print('\n================= UPDATE BOOK =================\n')
    book_id = get_id('Enter book_id to update:')
    cursor.execute('''
    SELECT
                   Books.book_id,
                   Books.title,
                   Books.total_copies,
                   Books.available_copies,
                   Author.author_name,
                   Genre.genre_name
    FROM Books
    JOIN Author ON Books.author_id = Author.id
    JOIN Genre ON Books.genre_id = Genre.id
    WHERE Books.book_id = ?''', (book_id,))

    book = cursor.fetchone()

    if not book:
        print('❌ Book not Found')
        conn.close()
        return
    
    headers = [desc[0] for desc in cursor.description]
    print(tabulate([book], headers,tablefmt = 'fancy_grid'))

    print("\nWhat do you want to update?")
    print("1. Title")
    print("2. Author")
    print("3. Genre")
    print("4. Total Copies")
    print("5. Available Copies")
    print("6. Cancel")

    choice = get_int('Enter your choice:')
    if choice == 1:
        new_title = input("Enter new title: ")
        cursor.execute("UPDATE Books SET title = ? WHERE book_id = ?", (new_title, book_id))

    elif choice == 2:
        new_author = input("Enter new author name: ")
        authorID = insertAuthor(conn,cursor,new_author)
        cursor.execute("UPDATE Books SET author_id = ? WHERE book_id = ?", (authorID, book_id))

    elif choice == 3:
        new_genre = input("Enter new genre: ")
        genreID = insertGenre(conn,cursor,new_genre)
        cursor.execute("UPDATE Books SET genre_id = ? WHERE book_id = ?", (genreID, book_id))

    elif choice == 4:
        new_total = get_int("Enter total copies: ")
        cursor.execute("UPDATE Books SET total_copies = ? WHERE book_id = ?", (new_total, book_id))

    elif choice == 5:
        new_available = get_int("Enter available copies: ")
        cursor.execute("UPDATE Books SET available_copies = ? WHERE book_id = ?", (new_available, book_id))

    else:
        print("Cancelled!")
        conn.close()
        return

    conn.commit()
    conn.close()
    print("✔ Book updated successfully!")

def delete_book():
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()

    print("\n================= DELETE BOOK =================\n")
    book_id = get_id("Enter Book ID to delete: ")

    # Check if book exists
    cursor.execute("SELECT title FROM Books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()

    if not book:
        print("❌ Book not found!")
        conn.close()
        return

    # Check if book is currently borrowed
    cursor.execute("""
        SELECT * FROM Borrow 
        WHERE book_id = ? AND return_date IS NULL
    """, (book_id,))
    borrowed = cursor.fetchone()

    if borrowed:
        print("❌ Cannot delete! Someone has borrowed this book.")
        conn.close()
        return

    confirm = input(f"Are you sure you want to delete '{book[0]}'? (Y/N): ").lower()
    if confirm == "y":
        cursor.execute("DELETE FROM Books WHERE book_id = ?", (book_id,))
        conn.commit()
        print("\n✔ Book deleted successfully!")
    else:
        print("\nDeletion cancelled.")

    conn.close()


def adminMenu(role):
    print(' WELCOME ADMIN... 😀')
    while True:
            print('\n1. VIEW ALL BOOKS')
            print('2. INSERT NEW BOOK')
            print('3. UPDATE BOOK DETAILS')
            print('4. DELETE A BOOK')
            print('5. VIEW MEMBERS')
            print('6. View Borrowed Books')
            print('7. View Borrowers by Book ID(not returned)')
            print('8. LOGOUT')
            ch = get_int('\nEnter the option:')
            if ch == 1:
                viewBooks(role)
            elif ch == 2 :
                insertBooks()
            elif ch == 3 :
                update_book()
            elif ch == 4 :
                delete_book()
            elif ch == 5 :
                viewMembers()
            elif ch == 6 :
                admin_borrowed_books()
            elif ch == 7 :
                view_members_by_bookID()
            elif ch == 8 :
                break
            else:
                print ('\nInvalid choice')


def loginAdmin(role):
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()
    
    print('\n================= ADMIN LOGIN =================\n')
    while True:
            
            username = input('Username : ')
            password = getpass('Password : ')
            cursor.execute('''
            SELECT member_id FROM MEMBERS WHERE username = ? AND  password = ? AND role = ?
        ''',(username,password,role))
            
            admin = cursor.fetchone()

            if admin :
                adminMenu(role)
                
            else:
                print ('Invalid Usename or Password')
            break     
                
    conn.commit()
    conn.close()

#.........................................LOGIN..........................................................#
def login():
    print ('\n\nWELCOME TO 📚 PAGE HAVEN LIBRARY 📖')
    
    while True:
        ch = get_int('\n1.Admin\n2.User\n3.Exit\n\nEnter the choice:')
        if ch == 1:
            loginAdmin('admin')
        elif ch == 2:
            loginUser()
        elif ch == 3:
            sys.exit()
        else:
            print('\n❌ Invalid Choice..')

   

        
login()



