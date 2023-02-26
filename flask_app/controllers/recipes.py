from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models import user
from flask_app.models import recipe
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def show_login_reg():
    if 'user_id' in session:
        session.clear()
    return render_template("login_reg.html")
@app.route('/register/user', methods = ['POST'])
def create_user():
    print(request.form)
    users = user.User.get_all()
    if not user.User.validate_user(request.form, users):
        return redirect ('/') 
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "fname": request.form['first_name'],
        "lname": request.form['last_name'],
        "email": request.form['email'],
        "password": pw_hash
    }
    user_id = user.User.save(data)
    session['user_id'] = user_id
    session['first_name'] = request.form['first_name']
    return redirect("/dashboard")
@app.route("/dashboard")
def show_dashboard():
    if 'user_id' not in session:
        flash("Must login or register")
        return redirect('/')
    data = {
        "id": session['user_id']
    }
    print(session['user_id'])
    return render_template("dashboard.html", user = user.User.get_user_with_recipes(data), recipes = recipe.Recipe.get_all_recipes_with_creator())
@app.route("/login/user", methods = ["POST"])
def check_login():
    # see if the username provided exists in the database
    data = { "email" : request.form["email"] }
    user_in_db = user.User.get_by_email(data)
    # user is not registered in the db
    if not user_in_db:
        flash("Invalid Email/Password")
        return redirect("/")
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        # if we get False after checking the password
        flash("Invalid Email/Password")
        return redirect('/')
    # if the passwords matched, we set the user_id into session
    session['user_id'] = user_in_db.id
    session['first_name'] = user_in_db.first_name
    # never render on a post!!!
    return redirect("/dashboard")
@app.route('/recipes/new')
def show_new_recipe():
    if 'user_id' in session:
        return render_template("new_recipe.html")
    else:
        flash("Must login or register")
        return redirect('/')
@app.route('/create/new/recipe', methods = ['POST'])
def create_new_recipe():
    print(request.form)
    if not recipe.Recipe.validate_recipe(request.form):
        return redirect('/recipes/new')
    data = {
        "name": request.form['name'],
        "under": request.form['under'],
        "description": request.form["description"],
        "instructions": request.form["instructions"],
        "date_made": request.form['date_made'],
        "user_id": session['user_id']
    }
    recipe_id = recipe.Recipe.save(data)
    return redirect('/dashboard')
@app.route('/recipes/<int:recipe_id>')
def show_recipe(recipe_id):
    print(session)
    data = {"id": recipe_id}
    return render_template('show_recipe.html', recipe = recipe.Recipe.get_recipe_with_creator(data))
@app.route('/delete/<int:recipe_id>')
def delete(recipe_id):
    data = {
        'id': recipe_id
    }
    recipe.Recipe.destroy(data)
    return redirect('/dashboard')
@app.route('/recipes/edit/<int:recipe_id>')
def show_edit(recipe_id):
    data = {"id": recipe_id}
    return render_template("edit_recipe.html", recipe = recipe.Recipe.get_one(data))
@app.route('/update/<int:recipe_id>', methods=['POST'])
def update(recipe_id):
    if not recipe.Recipe.validate_recipe(request.form):
        return redirect(f'/recipes/edit/{recipe_id}')
    data = {
        'id': recipe_id,
        "name":request.form['name'],
        "under": request.form['under'],
        "description": request.form['description'],
        "instructions": request.form['instructions'],
        "date_made": request.form['date_made']
    }
    recipe.Recipe.update(data)
    return redirect("/dashboard")
@app.route('/clear')
def clear_session():
    session.clear()
    return redirect('/')