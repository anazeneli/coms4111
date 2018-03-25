#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, g, redirect, url_for, abort, \
     render_template,session,flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
query_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queries.txt')
app = Flask(__name__, template_folder=tmpl_dir)
DATABASEURI = "postgresql://th2706:HuaTY720@35.231.44.137/proj1part2"
engine = create_engine(DATABASEURI)

def FetchQuery(target):
    file = open(query_dir)
    start = 0
    query = ''
    for line in file:
        if start == 1 and 'end' in line:
            break
        if start:
            query += line.strip() + ' '
        if target in line:
            start = 1
    return query

@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

@app.route('/')
def show_entries():
    if 'query' in session:
        query = session['query']
        if 'target' in session:
            target = session['target']
            if target == 'no preference':
                target = 'customers'
        else:
            target = None

        session.clear()
        if query:
            try:
                cur = g.conn.execute(query)
                keys = cur.keys()
                results = cur.fetchall()
                cur.close()
                entries = results
            except:
                entries = None
        else:
            entries = None
    else:
        entries = None
        target = None

    return render_template('show_entries.html', entries=entries, target = target)


@app.route('/search', methods=['POST'])
def search():
    myquery = request.form['query']
    session['query'] = myquery
    return redirect(url_for('show_entries'))

@app.route('/select', methods=['POST'])
def select():
    myquery = """select * from """+request.form.get('select')
    session['query'] = myquery
    flash('here are the results that you are looking for')
    return redirect(url_for('show_entries'))

@app.route('/advice', methods=['POST'])
def advice():
    atype = request.form.get('atype')
    target = request.form.get('target')
    myquery = FetchQuery(target)
    myquery = myquery.replace('TYPE', atype)
    session['query'] = myquery
    session['target'] = target
    flash('here are the suggested advertisement delivery methods')
    print('flashed')
    return redirect(url_for('show_entries'))

if __name__ == "__main__":
    import click


    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):

        """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.secret_key = 'super secret key'
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
    run()
