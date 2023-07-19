from flask import Flask
from webargs import fields
from webargs.flaskparser import use_args

from application.services.create_table import create_table
from application.services.db_connection import DBConnection

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return '/users/create?name=User`s name&phone=User`s phone number - create user<br>' \
           '/users/read-all - read all users<br>' \
           '/users/read/"User`s name" - read user by name<br>' \
           '/users/update/"User`s personal key" - update user by pk<br>' \
           '/users/delete/"User`s personal key" - delete user by pk<br>'


@app.route('/users/create')
@use_args({"name": fields.Str(required=True), "phone": fields.Int(required=True)}, location="query")
def create_user(args):
    with DBConnection() as connection:
        with connection:
            connection.execute(
                """
                INSERT INTO users (name, phone)
                VALUES (:name, :phone)
                """,
                ({"name": args["name"], "phone": args["phone"]})
            )
    return "User created"


@app.route('/users/read-all')
def read_all_users():
    with DBConnection() as connection:
        users = connection.execute("SELECT * FROM users;").fetchall()
    return "<br>".join([f" {user['pk']}: Name: {user['name']}  Phone number: {user['phone']}" for user in users])


@app.route('/users/read/<string:name>')
def read_user(name: str):
    with DBConnection() as connection:
        user = connection.execute("SELECT name, phone FROM users WHERE name = ?;", (name,)).fetchone()
    return "<br>".join([f"  Phone number: {user['phone']}"])


@app.route('/users/update/<int:pk>')
@use_args({"name": fields.Str(), "phone": fields.Int()}, location="query")
def update_user(args, pk: int):
    with DBConnection() as connection:
        with connection:
            name = args.get("name")
            phone = args.get("phone")

            if name is None and phone is None:
                return "No data to update"
            args_for_request = []

            if name is not None:
                args_for_request.append("name = :name")
            if phone is not None:
                args_for_request.append("phone = :phone")

            args_2 = ", ".join(args_for_request)

            connection.execute(
                f"""
                UPDATE users
                SET {args_2}
                WHERE pk = :pk
                """,
                ({"pk": pk, "name": name, "phone": phone})
            )
    return "User updated"


@app.route('/users/delete/<int:pk>')
def delete_user(pk: int):
    with DBConnection() as connection:
        with connection:
            connection.execute(
                f"""
                DELETE FROM users
                WHERE pk = :pk
                """,
                ({"pk": pk})
            )
    return "User deleted"


create_table()
if __name__ == '__main__':
    app.run()
