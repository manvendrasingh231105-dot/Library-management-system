from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

BOOKS_FILE = "books.txt"
ISSUED_FILE = "issued.txt"


def load_books():
    books = []
    if not os.path.exists(BOOKS_FILE):
        open(BOOKS_FILE, "a").close()

    with open(BOOKS_FILE, "r") as file:
        for line in file:
            parts = line.strip().split("|")
            if len(parts) == 4:
                books.append({
                    "id": parts[0],
                    "title": parts[1],
                    "author": parts[2],
                    "quantity": int(parts[3])
                })
    return books


def save_all_books(books):
    with open(BOOKS_FILE, "w") as file:
        for b in books:
            file.write(f"{b['id']}|{b['title']}|{b['author']}|{b['quantity']}\n")


def load_issued():
    issued = []
    if not os.path.exists(ISSUED_FILE):
        open(ISSUED_FILE, "a").close()

    with open(ISSUED_FILE, "r") as file:
        for line in file:
            parts = line.strip().split("|")
            if len(parts) == 3:
                issued.append({
                    "id": parts[0],
                    "title": parts[1],
                    "student": parts[2]
                })
    return issued


def save_issued_record(book_id, title, student_name):
    with open(ISSUED_FILE, "a") as file:
        file.write(f"{book_id}|{title}|{student_name}\n")


def save_all_issued(issued):
    with open(ISSUED_FILE, "w") as file:
        for i in issued:
            file.write(f"{i['id']}|{i['title']}|{i['student']}\n")


@app.route("/")
def home():
    return render_template("index.html", books=load_books())


@app.route("/add_book", methods=["POST"])
def add_book():
    book_id = request.form["id"]
    title = request.form["title"]
    author = request.form["author"]
    quantity = int(request.form["quantity"])

    books = load_books()
    for b in books:
        if b["id"] == book_id:
            return "Book ID already exists!", 400

    books.append({"id": book_id, "title": title, "author": author, "quantity": quantity})
    save_all_books(books)
    return redirect("/")


@app.route("/delete/<book_id>")
def delete_book(book_id):
    books = load_books()
    books = [b for b in books if b["id"] != book_id]
    save_all_books(books)
    return redirect("/")


@app.route("/edit/<book_id>")
def edit_book(book_id):
    books = load_books()
    for b in books:
        if b["id"] == book_id:
            return render_template("edit.html", book=b)
    return "Not Found", 404


@app.route("/update/<book_id>", methods=["POST"])
def update_book(book_id):
    title = request.form["title"]
    author = request.form["author"]
    quantity = int(request.form["quantity"])

    books = load_books()
    for b in books:
        if b["id"] == book_id:
            b["title"] = title
            b["author"] = author
            b["quantity"] = quantity
            break

    save_all_books(books)
    return redirect("/")


@app.route("/borrow/<book_id>", methods=["POST"])
def borrow(book_id):
    student = request.form["student"]
    books = load_books()

    for b in books:
        if b["id"] == book_id:
            if b["quantity"] > 0:
                b["quantity"] -= 1
                save_all_books(books)
                save_issued_record(book_id, b["title"], student)
                return redirect("/")
            else:
                return "Book not available!", 400

    return "Not Found", 404


@app.route("/issued")
def issued_list():
    return render_template("issued.html", issued=load_issued())


@app.route("/return/<book_id>/<student>")
def return_book(book_id, student):
    issued = load_issued()
    books = load_books()

    
    issued = [i for i in issued if not (i["id"] == book_id and i["student"] == student)]
    save_all_issued(issued)

    
    for b in books:
        if b["id"] == book_id:
            b["quantity"] += 1
            break

    save_all_books(books)
    return redirect("/issued")


if __name__ == "__main__":
    app.run(debug=True)
