from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user
db = "recipes"

class Recipe:
    def __init__( self , data ):
        self.id = data['id']
        self.name = data['name']
        self.under = data['under']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date_made = data['date_made']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.creator = None 
    
    @classmethod
    def get_all_recipes_with_creator(cls):
        # Get all tweets, and their one associated User that created it
        query = "SELECT * FROM recipes JOIN users ON recipes.user_id = users.id;"
        results = connectToMySQL(db).query_db(query)
        all_recipes = []
        for row in results:
            # Create a Tweet class instance from the information from each db row
            one_recipe = cls(row)
            # Prepare to make a User class instance, looking at the class in models/user.py
            one_recipe_user_info = {
                # Any fields that are used in BOTH tables will have their name changed, which depends on the order you put them in the JOIN query, use a print statement in your classmethod to show this.
                "id": row['users.id'], 
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }
            # Create the User class instance that's in the user.py model file
            creator = user.User(one_recipe_user_info)
            # Associate the Tweet class instance with the User class instance by filling in the empty creator attribute in the Tweet class
            one_recipe.creator = creator
            # Append the Tweet containing the associated User to your list of tweets
            all_recipes.append(one_recipe)
        return all_recipes
    @classmethod
    def save(cls, data):
        query = "INSERT INTO recipes (name, under, description, instructions, date_made, user_id) VALUES (%(name)s, %(under)s, %(description)s, %(instructions)s, %(date_made)s, %(user_id)s);"
        return connectToMySQL(db).query_db(query, data)
    @classmethod
    def get_one(cls,data):
        query = "SELECT * FROM recipes WHERE id = %(id)s;"
        results = connectToMySQL(db).query_db(query, data)
        return cls(results[0])
    @classmethod
    def update(cls,data):
        query = "UPDATE recipes SET name=%(name)s, under=%(under)s, description=%(description)s, instructions=%(instructions)s, date_made = %(date_made)s, updated_at = NOW() WHERE id = %(id)s;"
        return connectToMySQL(db).query_db(query,data)
    @classmethod
    def destroy(cls,data):
        query = "DELETE FROM recipes WHERE id = %(id)s;"
        return connectToMySQL(db).query_db(query,data)
    @classmethod
    def get_recipe_with_creator(cls, data):
        # Get all tweets, and their one associated User that created it
        query = "SELECT * FROM recipes JOIN users ON recipes.user_id = users.id WHERE recipes.id = %(id)s;"
        results = connectToMySQL(db).query_db(query,data)
        #all_recipes = []
            # Create a Tweet class instance from the information from each db row
        one_recipe = cls(results[0])
            # Prepare to make a User class instance, looking at the class in models/user.py
        one_recipe_user_info = {
                # Any fields that are used in BOTH tables will have their name changed, which depends on the order you put them in the JOIN query, use a print statement in your classmethod to show this.
            "id": results[0]['users.id'], 
            "first_name": results[0]['first_name'],
            "last_name": results[0]['last_name'],
            "email": results[0]['email'],
            "password": results[0]['password'],
            "created_at": results[0]['users.created_at'],
            "updated_at": results[0]['users.updated_at']
        }
            # Create the User class instance that's in the user.py model file
        creator = user.User(one_recipe_user_info)
            # Associate the Tweet class instance with the User class instance by filling in the empty creator attribute in the Tweet class
        one_recipe.creator = creator
            # Append the Tweet containing the associated User to your list of tweets
            #all_recipes.append(one_recipe)
        return one_recipe
    @staticmethod
    def validate_recipe(recipe):
        is_valid = True # we assume this is true
        if len(recipe['name']) < 3:
            flash("Name must be at least 3 characters.")
            is_valid = False
        if len(recipe['description']) < 3:
            flash("Description must be at least 3 characters.")
            is_valid = False
        if len(recipe['instructions']) < 3:
            flash("Instructions must be at least 3 characters")
            is_valid = False
        if len(recipe['date_made']) < 2:
            flash("Date Cooked/Made is required")
            is_valid = False
        if 'under' not in recipe:
            flash("Under 30 min must be selected!")
            is_valid = False
        return is_valid
    