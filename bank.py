from tkinter import *
from tkinter import messagebox
import sqlite3

# ---------------- DB ----------------
def connect():
    return sqlite3.connect("cat.db")

# ---------------- LOGIN ----------------
def validate_login(username, password):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT * FROM adminlogin WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    con.close()
    return row

def login_action():
    user = e1.get()
    pwd = e2.get()

    if validate_login(user, pwd):
        messagebox.showinfo("Login", "Success")
        login_win.destroy()
        menu()
    else:
        messagebox.showerror("Error", "Invalid credentials")

# ---------------- ACCOUNT CREATE ----------------
def create_account():
    acno = e1.get()
    name = e2.get()
    typ = e3.get()
    bal = e4.get()

    if not bal.isdigit():
        messagebox.showerror("Error", "Invalid balance")
        return

    con = connect()
    cur = con.cursor()
    cur.execute("INSERT INTO account VALUES(?,?,?,?)", (acno, name, typ, float(bal)))
    cur.execute("INSERT INTO transactions VALUES(?,?,?,?,?)", (acno, name, float(bal), 0.0, float(bal)))
    con.commit()
    con.close()

    messagebox.showinfo("Success", "Account created")

def create_ui():
    win = Toplevel()
    global e1, e2, e3, e4

    e1 = Entry(win); e1.pack()
    e2 = Entry(win); e2.pack()
    e3 = Entry(win); e3.pack()
    e4 = Entry(win); e4.pack()

    Button(win, text="Create", command=create_account).pack()

# ---------------- DEPOSIT ----------------
def deposit_action():
    acno = e1.get()
    try:
        amt = float(e2.get())
    except:
        messagebox.showerror("Error", "Invalid amount")
        return

    if amt <= 0:
        messagebox.showerror("Error", "Amount must be > 0")
        return

    con = connect()
    cur = con.cursor()

    cur.execute("SELECT acname, balance FROM account WHERE acno=?", (acno,))
    row = cur.fetchone()

    if not row:
        messagebox.showerror("Error", "Account not found")
        return

    name, bal = row
    cur.execute("UPDATE account SET balance=balance+? WHERE acno=?", (amt, acno))
    cur.execute("INSERT INTO transactions VALUES(?,?,?,?,?)", (acno, name, amt, 0.0, bal + amt))

    con.commit()
    con.close()

    messagebox.showinfo("Success", "Deposited")

def deposit_ui():
    win = Toplevel()
    global e1, e2

    e1 = Entry(win); e1.pack()
    e2 = Entry(win); e2.pack()

    Button(win, text="Deposit", command=deposit_action).pack()

# ---------------- WITHDRAW ----------------
def withdraw_action():
    acno = e1.get()
    try:
        amt = float(e2.get())
    except:
        messagebox.showerror("Error", "Invalid amount")
        return

    con = connect()
    cur = con.cursor()

    cur.execute("SELECT acname, balance FROM account WHERE acno=?", (acno,))
    row = cur.fetchone()

    if not row:
        messagebox.showerror("Error", "Account not found")
        return

    name, bal = row

    if amt > bal:
        messagebox.showerror("Error", "Insufficient balance")
        return

    cur.execute("UPDATE account SET balance=balance-? WHERE acno=?", (amt, acno))
    cur.execute("INSERT INTO transactions VALUES(?,?,?,?,?)", (acno, name, 0.0, amt, bal - amt))

    con.commit()
    con.close()

    messagebox.showinfo("Success", "Withdrawn")

def withdraw_ui():
    win = Toplevel()
    global e1, e2

    e1 = Entry(win); e1.pack()
    e2 = Entry(win); e2.pack()

    Button(win, text="Withdraw", command=withdraw_action).pack()

# ---------------- TRANSFER ----------------
def transfer_action():
    facno = e1.get()
    tacno = e2.get()

    try:
        amt = float(e3.get())
    except:
        messagebox.showerror("Error", "Invalid amount")
        return

    con = connect()
    cur = con.cursor()

    try:
        con.execute("BEGIN")

        cur.execute("SELECT acname, balance FROM account WHERE acno=?", (facno,))
        f = cur.fetchone()

        cur.execute("SELECT acname, balance FROM account WHERE acno=?", (tacno,))
        t = cur.fetchone()

        if not f or not t:
            raise Exception("Account not found")

        fname, fbal = f
        tname, tbal = t

        if amt > fbal:
            raise Exception("Insufficient balance")

        cur.execute("UPDATE account SET balance=balance-? WHERE acno=?", (amt, facno))
        cur.execute("UPDATE account SET balance=balance+? WHERE acno=?", (amt, tacno))

        cur.execute("INSERT INTO transactions VALUES(?,?,?,?,?)", (facno, fname, 0.0, amt, fbal - amt))
        cur.execute("INSERT INTO transactions VALUES(?,?,?,?,?)", (tacno, tname, amt, 0.0, tbal + amt))

        con.commit()
        messagebox.showinfo("Success", "Transferred")

    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))

    finally:
        con.close()

def transfer_ui():
    win = Toplevel()
    global e1, e2, e3

    e1 = Entry(win); e1.pack()
    e2 = Entry(win); e2.pack()
    e3 = Entry(win); e3.pack()

    Button(win, text="Transfer", command=transfer_action).pack()

# ---------------- MENU ----------------
def menu():
    win = Tk()

    Button(win, text="Create", command=create_ui).pack()
    Button(win, text="Deposit", command=deposit_ui).pack()
    Button(win, text="Withdraw", command=withdraw_ui).pack()
    Button(win, text="Transfer", command=transfer_ui).pack()

    win.mainloop()

# ---------------- LOGIN UI ----------------
login_win = Tk()

e1 = Entry(login_win)
e1.pack()

e2 = Entry(login_win, show="*")
e2.pack()

Button(login_win, text="Login", command=login_action).pack()

login_win.mainloop()
