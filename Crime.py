from flask import Flask, request, render_template, session
import sqlite3

from flask_session import Session
from werkzeug.utils import redirect
from datetime import date

folder = sqlite3.connect("report.db",check_same_thread=False)
listoftable1 = folder.execute("select * from sqlite_master where type = 'table' and name = 'crime'").fetchall()
listoftable2 = folder.execute("select * from sqlite_master where type = 'table' and name = 'user'").fetchall()

if listoftable1 !=[]:
    print("Crime table already exists")
else:
    folder.execute('''create table crime(
                            id integer primary key autoincrement,
                            description text,
                            remarks text,
                            date text);''')
    print("Table created")
if listoftable2 !=[]:
    print("user table already exists")
else:
    folder.execute('''create table user(
                            id integer primary key autoincrement,
                            name text,
                            address text,
                            email text,
                            phone integer,
                            password text);''')
    print("Table created")

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/',methods=['GET','POST'])
def Login_admin():
    if request.method == 'POST':
        getUsername = request.form["admname"]
        getPassword = request.form["admpass"]
        print(getUsername)
        print(getPassword)
        if getUsername == "admin" and getPassword == "12345":
            return redirect('/dashboard')
        else:
            return redirect('/')
    return render_template("login_admin.html")

@app.route('/dashboard')
def Admin_dashboard():
    return render_template("admindashboard.html")

@app.route('/view')
def View_report():
    cursor = folder.cursor()
    cursor.execute("select * from crime")

    result = cursor.fetchall()
    return render_template("viewallcrime.html",crime=result)


@app.route('/sort',methods=['GET','POST'])
def Search_crime():
    if request.method == 'POST':
        getDate = str(request.form["date"])
        cursor = folder.cursor()
        cursor.execute("select * from crime where date='"+getDate+"' ")
        result = cursor.fetchall()
        if result is None:
            print("There is no Crime on",getDate)
        else:
            return render_template("sortbydate.html",crime=result,status=True)
    else:
        return render_template("sortbydate.html",crime=[],status=False)



@app.route('/register',methods=['GET','POST'])
def User_register():
    if request.method == 'POST':
        getName = request.form["username"]
        getAddress = request.form["address"]
        getEmail = request.form["useremail"]
        getPhone = request.form["userphone"]
        getPass = request.form["userpass"]
        print(getName,getAddress,getEmail,getPhone)
        try:
            folder.execute("insert into user(name,address,email,phone,password) \
            values('"+getName+"','"+getAddress+"','"+getEmail+"',"+getPhone+",'"+getPass+"')")
            folder.commit()
            print("Inserted Successfully")
            return redirect('/complaint')
        except Exception as err:
            print(err)
    return render_template("userregister.html")

@app.route('/user',methods=['GET','POST'])
def Login_user():
    if request.method == 'POST':
        getEmail = request.form["useremail"]
        getPass = request.form["userpass"]
        cursor = folder.cursor()
        query = "select * from user where email='"+getEmail+"' and password='"+getPass+"' "
        result = cursor.execute(query).fetchall()
        if len(result)>0:
            for i in result:
                getName = i[1]
                getId = i[0]
                session["name"] = getName
                session["id"] = getId
                if (getEmail == i[3] and getPass == i[5]):
                    print("password correct")
                    return redirect('/usersession')

                else:
                    return render_template("userlogin.html",status=True)
    else:
        return render_template("userlogin.html",status=False)

@app.route('/userdashboard')
def user_dashboard():
    return render_template("userdashboard.html")

@app.route('/usersession')
def userpage():
    if not session.get("name"):
        return redirect('/')
    else:
        return render_template("usersession.html")


@app.route('/complaint',methods=['GET','POST'])
def Report_crime():
    if request.method == 'POST':
        getDescription = request.form["descrip"]
        getRemark = request.form["remark"]
        print(getDescription)
        print(getRemark)
        getDate = str(date.today())
        cursor = folder.cursor()
        query = "insert into crime(description,remarks,date) values('"+getDescription+"','"+getRemark+"','"+getDate+"')"
        cursor.execute(query)
        folder.commit()
        print(query)
        print("Inserted Successfully")
        return redirect('/user')
    return render_template("newcomplaint.html")

@app.route('/update',methods=['GET','POST'])
def Update_user():
    try:
        if request.method == 'POST':
            getname = request.form["newname"]
            print(getname)
            cursor = folder.cursor()
            count = cursor.execute("select * from user where name='" + getname + "' ")
            result = cursor.fetchall()
            print(len(result))
            return render_template("editprofile.html", searchname = result)
        return render_template("editprofile.html")
    except Exception as err:
        print(err)


@app.route('/edit',methods=['GET','POST'])
def User_edit():
    if request.method == 'POST':
        getName = request.form["newname"]
        getAddress = request.form["newaddress"]
        getEmail = request.form["newemail"]
        getPhone = request.form["newphone"]
        getPass = request.form["newpass"]
        try:
            query = "update user set address='" + getAddress + "',email='" + getEmail + "',phone=" + getPhone + ",password='" + getPass + "' where name='" + getName + "'"
            print(query)
            folder.execute(query)
            folder.commit()
            print("Edited Successfully")
            return redirect('/view')
        except Exception as error:
            print(error)

    return render_template("editprofile.html")

@app.route('/logout')
def Logout():
    session["name"] = None
    return redirect('/')



if __name__=="__main__":
    app.run()