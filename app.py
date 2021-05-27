from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
import os

#### Set FLASK_ENV variable to development mode.
os.environ['FLASK_ENV'] = 'development'


# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        return render_template("buggy-form.html")
    elif request.method == 'POST':
        header = "Buggy updated!"
        msg=""
        qty_wheels = request.form['qty_wheels'].strip()
        flag_color = request.form['flag_color'].strip()
        flag_color_secondary = request.form['flag_color_secondary'].strip()
        flag_pattern = request.form['flag_pattern'].strip()
        try:
            with sql.connect(DATABASE_FILE) as con:
                if not qty_wheels.isdigit():
                    raise ValueError("Wheel quantity must be a number!")
                elif len(flag_color) > 20:
                    raise ValueError("Primary flag colour must be less than 20 characters!")
                elif len(flag_color_secondary) > 20:
                    raise ValueError("Secondary flag colour must be less than 20 characters!")
                elif len(flag_pattern) > 20:
                    raise ValueError("Flag pattern must be less than 20 characters!")

                cur = con.cursor()
                cur.execute(
                    """UPDATE buggies SET qty_wheels=?,
                                        flag_color=?,
                                        flag_color_secondary=?,
                                        flag_pattern=? WHERE id=?""",
                    (qty_wheels, flag_color, flag_color_secondary, flag_pattern, DEFAULT_BUGGY_ID)
                )
                con.commit()
                msg = "Record successfully saved."
        except ValueError as e:
            header = "Validation error!"
            msg = str(e)
        except:
            con.rollback()
            header = "SQL error!"
            msg = "Error in update operation."
        finally:
            con.close()
        return render_template("updated.html", header = header, msg = msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")

#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0", port=21999)
