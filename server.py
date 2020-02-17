from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import connectToMySQL
import re
from datetime import datetime
from flask_bcrypt import Bcrypt        
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/register")
def reg():
    return render_template("register_login.html")
    
@app.route("/register", methods=["POST"])
def register():
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    valid = True
    if len(request.form["fname"])<1:
        valid = False
        flash("First Name is required")

    elif len(request.form["fname"])<2:
        valid = False
        flash("First Name must be at least 2 characters long")

    elif not request.form["fname"].isalpha():
        valid = False
        flash("First Name should contains only letters")
    
    if len(request.form["lname"])<1:
        valid = False
        flash("Last Name is required")

    elif len(request.form["lname"])<2:
        valid = False
        flash("Last Name must be at least 2 characters long")

    elif not request.form["lname"].isalpha():
        valid = False
        flash("Last Name should contains only letters")

    if len(request.form["password"])<1:
        valid = False
        flash("Password is required")
    elif len(request.form["password"])<8:
        valid = False
        flash("Password should contains more than 8 letters")

    elif request.form["password"] != request.form["confirm_password"]:
        valid = False
        flash("Password and Confirm Password must match")

    if len(request.form["email"])<1:
        valid = False
        flash("Email is required")
    elif not EMAIL_REGEX.match(request.form['email']):
        valid = False
        flash("Invalid email address!")
    mysql = connectToMySQL('thoughts')
    
    if valid :
        pass_hash = bcrypt.generate_password_hash(request.form["password"])
        query = "Insert into users(first_name,last_name,email,password,created_at) values(%(fn)s, %(ln)s, %(em)s,%(pw)s,%(created_at)s);"
        data = {
            "fn": request.form["fname"],
            "ln": request.form["lname"],
            "em": request.form["email"],
            "pw": pass_hash,
            "created_at":datetime.now()
        }
        new_user = mysql.query_db(query, data)
        session['user_id'] = new_user
        session['name']=request.form["fname"]
        session['lname']=request.form["lname"]
       
        return redirect("/index")
    return redirect("/register")

@app.route('/login', methods=["POST"])
def login():
   
    mysql = connectToMySQL("thoughts")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email" : request.form["email"] }
    result = mysql.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
           
            session['user_id'] = result[0]['id']
            session['name']=result[0]['first_name']
            session['lname']=result[0]['last_name']
            
            return redirect("/index")
        else :
            flash("Password incorrect!")
        return redirect("/")

    flash("This user don't exist!")
    return redirect("/")

@app.route('/index')
def success():
    mysql = connectToMySQL('thoughts')
    select = "select u.first_name, u.last_name, t.created_at, t.user_id, thought, thought_id, count(*) as nr_likes from  thoughts t inner join users u on t.user_id= u.id inner join likes l on t.id = l.thought_id group by thought_id order by nr_likes desc;"
    thoughts = mysql.query_db(select)

    mysql = connectToMySQL('thoughts')
    query = "Select u.first_name, u.last_name, t.created_at, t.user_id, t.id ,thought from thoughts t inner join users u on t.user_id= u.id where t.id not in (select thought_id from likes);"
   
    unliked_thoughts = mysql.query_db(query)
    print(unliked_thoughts)
    print(thoughts)

    mysql = connectToMySQL('thoughts')
    select_query = "Select * from likes where user_id = %(user_id)s"
    data3 = {
        "user_id":session["user_id"]
    }
    select_likes = mysql.query_db(select_query,data3)
    likes = []
    for i in select_likes:
        likes.append(i['thought_id'])

    mysql = connectToMySQL('thoughts')
    user_notifications = "Select count(*) as notify from notifications where confirm = 0 and user_to_notify_id = %(user_id)s"

    user_notifications = mysql.query_db(user_notifications,data3)
    print(user_notifications)

    return render_template('index.html', thoughts=thoughts, unliked_thoughts=unliked_thoughts , likes=likes , user_notifications = user_notifications)

@app.route('/thoughts', methods=["POST"])
def submit():
    valid = True
    if len(request.form["thought"])<1:
        valid = False
        flash("Thought is required")
    elif len(request.form["thought"])<5:
        valid = False
        flash("Thought must be at least 5 characters")
    if valid:
        mysql = connectToMySQL('thoughts')
        query = "Insert into thoughts(thought,user_id,created_at) values(%(thought)s, %(user_id)s,%(created_at)s);"
        data = {
            "thought": request.form["thought"],
            "user_id": request.form["user_id"],
            "created_at":datetime.now()
        }
        new_thought = mysql.query_db(query, data)
        flash("Success")
    return redirect('/index')

@app.route('/thought/<id>')
def thought(id):
    mysql = connectToMySQL('thoughts')
    query = "Select * from thoughts where id = %(id)s;"
    data = {
        "id" :id
    }
    thought = mysql.query_db(query, data)

    mysql = connectToMySQL('thoughts')
    select_query = "Select * from likes where user_id = %(user_id)s"
    data3 = {
        "user_id":session["user_id"]
    }
    select_likes = mysql.query_db(select_query,data3)
    likes = []
    for i in select_likes:
        likes.append(i['thought_id'])
    
    mysql = connectToMySQL('thoughts')
    query = "select first_name , last_name, l.user_id from users u inner join likes l on u.id = l.user_id where l.thought_id=%(id)s and l.user_id!=%(user_id)s;"
    data = {
        "id" :id,
        "user_id": session['user_id']
    }
    users_likes = mysql.query_db(query, data)

    mysql = connectToMySQL('thoughts')
    query = "select first_name , last_name, l.user_id from users u inner join likes l on u.id = l.user_id where l.thought_id= %(id)s and l.user_id= %(user_id)s;"
    data = {
        "id" :id,
        "user_id": session['user_id']
    }
    current_user = mysql.query_db(query, data)
    
    mysql = connectToMySQL('thoughts')
    user_notifications = "Select count(*) as notify from notifications where confirm = 0 and user_to_notify_id = %(user_id)s"

    user_notifications = mysql.query_db(user_notifications,data3)
    print(user_notifications)

    return render_template('likes.html', thought=thought[0] , likes=likes, users= users_likes, current=current_user , user_notifications=user_notifications)

@app.route('/destroy')
def destroy():
    session.clear()	
    return redirect('/')

@app.route('/delete/<id>')
def delete(id):
    mysql = connectToMySQL('thoughts')
    query = "Delete from thoughts where id = %(id)s;"
    data = { "id":id}
    delete_thoughts = mysql.query_db(query,data)
    flash("Deleted Sucessfully")
    return redirect('/index')

@app.route('/like/<id>/<user_id>/<user_to_notify>')
def likes(id,user_id,user_to_notify):
    data = {
            "thought_id":id,
            "user_id":user_id,
            "created_at":datetime.now()
        }
    mysql = connectToMySQL('thoughts')
    query = "Insert into likes(thought_id,user_id,created_at) values(%(thought_id)s, %(user_id)s, %(created_at)s);"
    new_like = mysql.query_db(query, data)

    data2 = {
            "thought_id":id,
            "user_to_notify_id":user_to_notify,
            "notifier_id":user_id,
            "created_at":datetime.now()
        }

    mysql = connectToMySQL('thoughts')
    query2 = "Insert into notifications(thought_id,user_to_notify_id,notifier_id,created_at) values(%(thought_id)s, %(user_to_notify_id)s,%(notifier_id)s, %(created_at)s);"
    notifications = mysql.query_db(query2, data2)

    return redirect('/index')

@app.route('/unlike/<id>/<user_id>')
def unlikes(id,user_id):
    data = {
            "thought_id":id,
            "user_id":user_id
        }
    mysql = connectToMySQL('thoughts')
    query = "Delete from likes where thought_id = %(thought_id)s and user_id = %(user_id)s;"
    unlike = mysql.query_db(query, data)

    return redirect('/index')

@app.route('/user/<id>')
def user(id):
    data = {
        "id":id
    }
    mysql = connectToMySQL('thoughts')
    select = "select u.first_name, u.last_name, t.created_at, t.user_id, thought, thought_id, count(*) as nr_likes from  thoughts t inner join users u on t.user_id= u.id inner join likes l on t.id = l.thought_id where t.user_id = %(id)s group by thought_id order by t.created_at desc;"
    thoughts = mysql.query_db(select,data)

    mysql = connectToMySQL('thoughts')
    query = "Select u.first_name, u.last_name, t.created_at, t.user_id, t.id ,thought from thoughts t inner join users u on t.user_id= u.id where t.user_id = %(id)s and t.id not in (select thought_id from likes);"
   
    unliked_thoughts = mysql.query_db(query,data)
    print(unliked_thoughts)
    print(thoughts)

    mysql = connectToMySQL('thoughts')
    select_query = "Select * from likes where user_id = %(user_id)s;"
    data3 = {
        "user_id":session["user_id"]
    }
    select_likes = mysql.query_db(select_query,data3)
    likes = []
    for i in select_likes:
        likes.append(i['thought_id'])


    mysql = connectToMySQL('thoughts')
    user1 = "Select first_name, last_name from users where id = %(id)s;"
    data = {
        "id":id
    }
    user = mysql.query_db(user1,data)
    print(user)
    mysql = connectToMySQL('thoughts')
    user_notifications = "Select count(*) as notify from notifications where confirm = 0 and user_to_notify_id = %(user_id)s"

    user_notifications = mysql.query_db(user_notifications,data3)
    print(user_notifications)
    

    return render_template('user.html', thoughts=thoughts, unliked_thoughts=unliked_thoughts , likes=likes , user=user, user_notifications=user_notifications)

@app.route('/notifications/<user_to_notify_id>')
def notifications(user_to_notify_id):
    data = {
             "user_to_notify_id":user_to_notify_id,
        }
    mysql = connectToMySQL('thoughts')
    query = "Update notifications set confirm = 1 where user_to_notify_id = %(user_to_notify_id)s;"
    notification = mysql.query_db(query, data)

    mysql = connectToMySQL('thoughts')
    query2 = "Select u.first_name, u.last_name, n.created_at, n.thought_id from notifications n inner join thoughts t on n.thought_id=t.id inner join users u on u.id=n.notifier_id where user_to_notify_id = %(user_to_notify_id)s order by n.created_at desc;"
    notifications = mysql.query_db(query2, data)
    print(notifications)
    data3 = {
             "user_id":session['user_id'],
        }
    mysql = connectToMySQL('thoughts')
    user_notifications = "Select count(*) as notify from notifications where confirm = 0 and user_to_notify_id = %(user_id)s"

    user_notifications = mysql.query_db(user_notifications,data3)
    print(user_notifications)

    now = datetime.now()
    #now = now.strftime("%d.%m.%Y %H:%M:%S")
    times = []
    for notification in notifications:

        notify_time = notification['created_at']
        diff = now - notify_time
        days = diff.days
        seconds = diff.seconds
        hours = int(seconds/3600)
        full_minutes = seconds/60
        minutes = int(full_minutes)%60
        weeks = int(days/7)
        time = {
            "weeks":weeks,
            "days":days,
            "hours":hours,
            "minutes":minutes
        }
        times.append(time)
        print(time)

    nots =[]
    for n in range(len(notifications)):
        nots.append(notifications[n])
        nots[n]['weeks']=times[n]['weeks']
        nots[n]['days']=times[n]['days']
        nots[n]['hours']=times[n]['hours']
        nots[n]['minutes']=times[n]['minutes']
    print(nots)

    return render_template('notifiations.html', notifications = nots , user_notifications=user_notifications , times=times)

@app.route('/notifications/thought/<id>')
def notify(id):

    data = {
             "id":id,
        }

    mysql = connectToMySQL('thoughts')
    thought = "select u.first_name, u.last_name, t.created_at, t.user_id, thought, thought_id, count(*) as nr_likes from  thoughts t inner join users u on t.user_id= u.id inner join likes l on t.id = l.thought_id where t.id = %(id)s group by thought_id;"
   
    thought = mysql.query_db(thought, data)

    data3 = {
             "user_id":session['user_id'],
        }

    mysql = connectToMySQL('thoughts')
    select_query = "Select * from likes where user_id = %(user_id)s;"
    select_likes = mysql.query_db(select_query,data3)
    likes = []
    for i in select_likes:
        likes.append(i['thought_id'])
    
    mysql = connectToMySQL('thoughts')
    user_notifications = "Select count(*) as notify from notifications where confirm = 0 and user_to_notify_id = %(user_id)s"

    user_notifications = mysql.query_db(user_notifications,data3)
    print(user_notifications)

    return render_template('thought.html', thoughts = thought , likes=likes , user_notifications=user_notifications)

@app.route('/search_user', methods=['POST'])
def search():
    keyword = request.form['search']
    print(len(keyword))
    full_name = keyword.split(' ')
    print(full_name)
    mysql = connectToMySQL('thoughts')
    results = ()
    if len(keyword)==0:
        results = ()
    else:
        query = "Select first_name, last_name, id from users where first_name like '{}%';".format(keyword)
        results = mysql.query_db(query)
    print(results)
    return render_template('partials/users.html', results=results)

if __name__ == "__main__":
    app.run(debug=True)

