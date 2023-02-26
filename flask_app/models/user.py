from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import recipe
import datetime
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
db = "recipes"

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.recipes = []
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        # make sure to call the connectToMySQL function with the schema you are targeting.
        results = connectToMySQL(db).query_db(query)
        # Create an empty list to append our instances of friends
        users = []
        # Iterate over the db results and create instances of friends with cls.
        for user in results:
            users.append( cls(user) )
        return users
    @classmethod
    def save(cls, data):
        query = "INSERT INTO users ( first_name, last_name, email, password) VALUES (%(fname)s, %(lname)s, %(email)s, %(password)s);"
        return connectToMySQL(db).query_db(query, data)
    @classmethod
    def get_one(cls,data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        results = connectToMySQL(db).query_db(query, data)
        return cls(results[0])
    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL(db).query_db(query,data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0])
    @classmethod
    def get_user_with_recipes( cls , data ):
        query = "SELECT * FROM users LEFT JOIN recipes ON recipes.user_id = users.id WHERE users.id = %(id)s;"
        results = connectToMySQL(db).query_db( query , data )
        # results will be a list of topping objects with the burger attached to each row. 
        user = cls( results[0] )
        for row_from_db in results:
            # Now we parse the burger data to make instances of burgers and add them into our list.
            recipe_data = {
                "id" : row_from_db["recipes.id"],
                "name" : row_from_db["name"],
                "under" : row_from_db["under"],
                "description" : row_from_db["description"],
                "instructions" : row_from_db["instructions"],
                "date_made": row_from_db['date_made'],
                "created_at" : row_from_db["recipes.created_at"],
                "updated_at" : row_from_db["recipes.updated_at"],
                "user_id": row_from_db["user_id"]
            }
            user.recipes.append( recipe.Recipe(recipe_data ) )
        return user

    @staticmethod
    def validate_user(user, users):
        is_valid = True # we assume this is true
        for u in users:
            if u.first_name == user['first_name'] and u.last_name == user['last_name']:
                flash("You are already registered")
                is_valid = False
                break
        if len(user['first_name']) < 2:
            flash("First name must be at least 2 characters.")
            is_valid = False
        if len(user['last_name']) < 2:
            flash("Last name must be at least 2 characters.")
            is_valid = False
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!")
            is_valid = False
        password = user['password']
        password_list = [*password]
        print(password_list)
        has_upper = False
        has_number = False
        for character in password_list:
            if character.isupper() == True:
                has_upper = True
                continue
            if character.isnumeric() == True:
                has_number = True
                continue
        if not has_upper or not has_number:
            flash("Password must have at least one capital letter and one number")
            is_valid = False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters long")
            is_valid = False
        if user['password'] != user['confirm']:
            flash("Invalid password")
            is_valid = False
        for u in users:
            if user['email'] == u.email:
                flash("Email is already taken.  Please use another one")
                is_valid = False
                break
        return is_valid