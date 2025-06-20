import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta

class LibraryItem:
    def __init__(self, title, total_copies=1):
        self.title = title
        self.popularity = 0
        self.total_copies = total_copies
        self.borrowed_copies = 0

    def is_available(self):
        return self.total_copies > self.borrowed_copies

    def borrow(self):
        if self.is_available():
            self.borrowed_copies += 1
            self.popularity += 1
            return True
        return False

    def return_item(self):
        if self.borrowed_copies > 0:
            self.borrowed_copies -= 1

class Book(LibraryItem):
    def __init__(self, title, total_copies, loan_period_seconds=15):
        super().__init__(title, total_copies)
        self.loan_period = timedelta(seconds=loan_period_seconds)

class DVD(LibraryItem):
    pass

class Magazine(LibraryItem):
    pass

class Software(LibraryItem):
    def __init__(self, title):
        super().__init__(title, total_copies=float('inf'))

class Loan:
    def __init__(self, item, borrow_datetime):
        self.item = item
        self.borrow_date = borrow_datetime
        self.due_date = borrow_datetime + item.loan_period if isinstance(item, Book) else None
        self.returned = False
        self.return_date = None
        self.fine = 0.0

    def return_item(self, return_datetime):
        self.return_date = return_datetime
        self.returned = True
        self.item.return_item()

        if isinstance(self.item, Book) and return_datetime > self.due_date:
            overdue_seconds = (return_datetime - self.due_date).total_seconds()
            self.fine = round(overdue_seconds * 0.01, 2)

        return self.fine

class LibraryMember:
    def __init__(self, name):
        self.name = name
        self.loans = []

    def borrow_item(self, library, item_title):
        item = library.get_item(item_title)
        if item:
            if isinstance(item, Software) and any(l.item.title == item_title for l in self.loans if not l.returned):
                return f"Oled juba võtnud '{item_title}'."

            if item.borrow():
                loan = Loan(item, datetime.now())
                self.loans.append(loan)
                return f"Sa võtsid '{item_title}'."
            else:
                return f"'{item_title}' pole hetkel saadaval."

    def return_item(self, item_title):
        for loan in self.loans:
            if loan.item.title == item_title and not loan.returned:
                fine = loan.return_item(datetime.now())
                self.loans.remove(loan)
                if fine > 0:
                    return f"Sa tagastasid toote '{item_title}' hilinenult. Trahv: {fine} €."
                return f"Sa tagastasid '{item_title}'."

    def view_loans(self):
        report = []
        for loan in self.loans:
            if not loan.returned:
                report.append(f"{loan.item.title} (võetud)")
        return report

class Library:
    def __init__(self):
        self.items = {}
        self.members = []

    def add_item(self, item):
        self.items[item.title] = item

    def get_item(self, title):
        return self.items.get(title)

    def add_member(self, member):
        self.members.append(member)

    def top_popular_items(self, n=10):
        return sorted(self.items.values(), key=lambda x: x.popularity, reverse=True)[:n]

    def list_available_items(self):
        return [item for item in self.items.values() if item.is_available()]

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Raamatukogu")
        self.geometry("600x450")

        self.library = Library()
        self.init_library()
        self.member = None
        self.ask_username()

        self.create_widgets()
        self.update_available_list()
        self.update_loans_list()
        self.update_popular_list()

        self.check_overdue_loans()

    def ask_username(self):
        name = simpledialog.askstring("Sissepääs", "Sisestage oma nimi:")
        if not name:
            self.destroy()
        else:
            self.member = LibraryMember(name)
            self.library.add_member(self.member)

    def init_library(self):
        self.library.add_item(Book("Harry Potter", 8))
        self.library.add_item(Book("1984", 6))
        self.library.add_item(Book("Sõda ja rahu", 12))
        self.library.add_item(DVD("Tähtedevaheline", 6))
        self.library.add_item(DVD("Maatriks", 9))
        self.library.add_item(Magazine("Teadus ja elu", 5))
        self.library.add_item(Magazine("Üle maailma", 7))
        self.library.add_item(Software("Photoshop"))
        self.library.add_item(Software("AutoCAD"))
        self.library.add_item(Software("Microsoft Office"))

    def create_widgets(self):
        tk.Label(self, text="Saadaolevad kaubad:").grid(row=0, column=0, sticky="w")
        self.available_list = tk.Listbox(self, width=30, height=10)
        self.available_list.grid(row=1, column=0, padx=5)

        self.borrow_btn = tk.Button(self, text="Võta valitud element", command=self.borrow_selected)
        self.borrow_btn.grid(row=2, column=0, pady=5)

        tk.Label(self, text="Teie laenud:").grid(row=0, column=1, sticky="w")
        self.loans_list = tk.Listbox(self, width=40, height=10)
        self.loans_list.grid(row=1, column=1, padx=5)

        self.return_btn = tk.Button(self, text="Tagasta valitud element", command=self.return_selected)
        self.return_btn.grid(row=2, column=1, pady=5)

        tk.Label(self, text="10 populaarseimat:").grid(row=3, column=0, sticky="w")
        self.popular_list = tk.Listbox(self, width=70, height=8)
        self.popular_list.grid(row=4, column=0, columnspan=2, padx=5)

    def update_available_list(self):
        self.available_list.delete(0, tk.END)
        for item in self.library.list_available_items():
            copies = item.total_copies - item.borrowed_copies
            self.available_list.insert(tk.END, f"{item.title} (saadaval: {copies})")

    def update_loans_list(self):
        self.loans_list.delete(0, tk.END)
        for loan in self.member.view_loans():
            self.loans_list.insert(tk.END, loan)

    def update_popular_list(self):
        self.popular_list.delete(0, tk.END)
        top = self.library.top_popular_items()
        for item in top:
            self.popular_list.insert(tk.END, f"{item.title} — populaarne: {item.popularity}")

    def borrow_selected(self):
        selection = self.available_list.curselection()
        if not selection:
            messagebox.showwarning("Viga", "Valige ese, mida võtta.")
            return
        title = self.available_list.get(selection[0]).split(" (")[0]
        result = self.member.borrow_item(self.library, title)
        messagebox.showinfo("Tulemus", result)
        self.refresh_all()

    def return_selected(self):
        selection = self.loans_list.curselection()
        if not selection:
            messagebox.showwarning("Viga", "Valige tagastatav toode.")
            return
        loan_str = self.loans_list.get(selection[0])
        title = loan_str.split(" (")[0]
        result = self.member.return_item(title)
        messagebox.showinfo("Tulemus", result)
        self.refresh_all()

    def refresh_all(self):
        self.update_available_list()
        self.update_loans_list()
        self.update_popular_list()

    def check_overdue_loans(self):
        overdue_items = []
        now = datetime.now()

        for loan in self.member.loans:
            if isinstance(loan.item, Book) and not loan.returned and loan.due_date < now:
                overdue_seconds = int((now - loan.due_date).total_seconds())
                overdue_items.append(f"{loan.item.title} — {overdue_seconds} sek hilinenud")

        if overdue_items:
            messagebox.showwarning("Märguanne", "Sul on hilinenud laene:\n" + "\n".join(overdue_items))

        self.refresh_all()
        self.after(5000, self.check_overdue_loans)

app = LibraryApp()
app.mainloop()
