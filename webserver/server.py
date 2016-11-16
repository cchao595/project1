#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from spotify_queries.py import *


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the postgresql test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/postgres
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# Swap out the URI below with the URI for the database created in part 2
DATABASEURI = "postgresql://cc4059:u6t7u@104.196.175.120/postgres"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);"""
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  #print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT a.name FROM Follows AS f, Artists AS a WHERE f.artist_id = a.artist_id GROUP BY f.artist_id, a.name ORDER BY count(*) desc LIMIT 5")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT s.title FROM Listens as l, Songs AS s WHERE l.song_id = s.song_id GROUP BY l.song_id, s.title ORDER BY count(*) desc LIMIT 5")
  songs = []
  for result in cursor:
    songs.append(result['title'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT a.name FROM Albums as a ORDER BY a.year desc LIMIT 5")
  albums = []
  for result in cursor:
    albums.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names, data1 = songs, data2 = albums)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/userprofiles')
def userprofiles():
  cursor = g.conn.execute("SELECT U.user_id FROM GeneralUsers AS G, Users AS U WHERE G.user_id = U.user_id")
  userids = []
  infoperuser = []
  for result in cursor:
    userids.append(result['user_id'])  # can also be accessed using result[0]
  cursor.close()
  for user in userids:
    cmd = "SELECT U.username, U.dob, U.email FROM GeneralUsers AS G, Users AS U WHERE U.user_id = :name1"
    cmd2 = "SELECT DISTINCT P.title FROM PersonalPlaylists_manages AS P WHERE P.user_id = :name1"
    cmd3 = "SELECT DISTINCT a.name FROM Follows AS f, Artists as a WHERE f.user_id = :name1 and a.artist_id = f.artist_id"
    cmd0 = "SELECT DISTINCT l.library_index, l.library_name From Albums as a, library_adds as l where l.user_id = :name1 and l.album_id = a.album_id"
    cursor2 = g.conn.execute(text(cmd), name1 = user)
    cursor3 = g.conn.execute(text(cmd2), name1 = user)
    cursor = g.conn.execute(text(cmd3), name1 = user)
    cursor0 = g.conn.execute(text(cmd0), name1 = user)
    # assign a row of data to "row" (username, dob, email)
    row = cursor2.fetchone()
    # append each item in "row" (containing username, dob, email) to infoperuser
    for item in row:
      infoperuser.append(item)
    # place list of distinct artist names into variable row1
    row1 = cursor.fetchall()
    # start a string that will detail all the artists followed by this userid
    str2 = 'Follows: '
    # add each artist name to the string; row1 is list of artist names
    for item1 in row1:
      follow = []
      # this for loop seems unnecessary, there is only 1 object in item1
      for w in item1:
        follow.append(w)
        
      str2 += ' '.join(str(e)+ ' ' for e in follow)
    infoperuser.append(str2)
    cursor.close()
    row0 = cursor0.fetchall()
    infoperuser.append('Libraries: ')
    for item0 in row0:
      indexes = []
      libraryname = []
      for x in item0:
        libraryname.append(x)
      indexes.append(libraryname[0])
      str0 = '. '.join(str(e) for e in libraryname)
      infoperuser.append(str0)
      for i in indexes:
        cmdalbums = "SELECT a.name from  Albums as A, library_adds as l where l.user_id = :name1 and a.album_id = l.album_id and l.library_index = :ind"
        cursora = g.conn.execute(text(cmdalbums), name1 = user, ind = i)
        for result in cursora:
          infoperuser.append(result['name'])
        cursora.close()
    cursor0.close();
    
    row2 = cursor3.fetchall()
    infoperuser.append('Playlists: ')
    for item2 in row2:     
      for x in item2:
        infoperuser.append(x)
        infoperuser.append('Title Artist Length(s) Explicit')
        cmd3 = "SELECT s.title, a.name, s.song_length/1000 as length, s.explicit from songs as s, artists as a, personalplaylists_manages as p, records as r where p.title = :name3 and p.song_id = s.song_id and p.song_id = r.song_id and a.artist_id = r.artist_id"
        cursor4 = g.conn.execute(text(cmd3), name3 = x)
        row3 = cursor4.fetchall()
        # each item3 is a tuple of title, name, song length, explicit
        for item3 in row3:
          songinfo = []
          # this loop allows item3 to be made into an array
          for y in item3:
            songinfo.append(y)
          str1 = ' '.join(str(e) for e in songinfo)
          infoperuser.append(str1)
        cursor4.close()

  cursor3.close()
  cursor2.close()
  context = dict(data = infoperuser)

  return render_template("userprofiles.html", **context)

@app.route('/artists')
def artists():
  cursor = g.conn.execute("SELECT A.artist_id FROM artists as A")
  artists = []
  infoperartist = []
  for result in cursor:
    artists.append(result['artist_id'])  # can also be accessed using result[0]
  cursor.close()
  for artist in artists:
    cmd = "SELECT A.name, A.genre FROM artists AS A WHERE A.artist_id = :name1"
    cmd2 = "SELECT B.name, B.year, B.no_of_songs, S.studio_name FROM albums as B, affiliated as A, studio as S, produces as P WHERE A.artist_id = :name2 and S.studio_id = P.studio_id and P.album_id = B.album_id"
    cursor2 = g.conn.execute(text(cmd), name1 = artist)
    cursor3 = g.conn.execute(text(cmd2), name2 = artist)
    row = cursor2.fetchall()
    for item in row:
      artistinfo = []
      for x in item:
        artistinfo.append(x)
      str1 = '- '.join(str(e) for e in artistinfo)
      infoperartist.append(str1)
    row2 = cursor3.fetchall()
    infoperartist.append('Albums')
    for item2 in row2:
      infoperartist.append('Album Name, Year Released, No of Songs, Record Label')
      albuminfo = []     
      for y in item2:     
        albuminfo.append(y)
      str2 = ' '.join(str(e) for e in albuminfo)
      cmd3 = "SELECT DISTINCT s.title, a.name, s.song_length/1000 as length, s.explicit from songs as s, artists as a, contains as c, albums as b, affiliated as r, records as d, produces as p WHERE B.album_id =c.album_id and b.name = :name3 and s.song_id = c.song_id and p.album_id = b.album_id and a.artist_id = r.artist_id and c.song_id = d.song_id and a.artist_id = d.artist_id"
      cursor4 = g.conn.execute(text(cmd3), name3 = albuminfo[0])
      infoperartist.append(str2)
      infoperartist.append('Songs in the Album:')
      infoperartist.append('Title Artist Length(s) Explicit')
      row3 = cursor4.fetchall()
      for item3 in row3:
        songs = []
        for z in item3:
          songs.append(z)
        str3 = ' '.join(str(e) for e in songs)
        infoperartist.append(str3)

  cursor3.close()
  cursor2.close()
  context = dict(data = infoperartist)
  
  return render_template("artists.html", **context)

@app.route('/gandm')
def gandm():
  cursor = g.conn.execute("SELECT g.gm_id FROM genresmoods as g")
  # SQL query: Fetch genre/mood ids
  gmIds = []
  infoPerGm = []
  for result in cursor:
    gmIds.append(result['gm_id'])  # can also be accessed using result[0]
  cursor.close()
  # for each gm_id
  for anId in gmIds:
    # get gm name and description
    cmd1 = "SELECT g.gm_name, g.gm_description FROM genresmoods As g WHERE g.gm_id = :name1"
    cursor1 = g.conn.execute(text(cmd1), :name1 = anId)
    row = cursor1.fetchall()
    # print gm title and description
    for item in row:
      gminfo = []
      for x in item:
        gminfo.append(x)
      str1 = ' - '.join(str(e) for e in gminfo)
      infoPerGm.append(str1)
    cursor1.close()
    # get playlist titles and description
    cmd2 = "SELECT DISTINCT p.title, p.description FROM publicplaylists_generates AS p, gathers AS g WHERE g.gm_id = :name2 AND g.publicplaylist_id = p.publicplaylist_id"
    cursor2 = g.conn.execute(text(cmd2), :name2 = anId)
    row = cursor2.fetchall()
    # print line "Public Playlists:"
    infoPerGm.append('Public Playlists: ')
    # for each public playlist
    for item in row:     
      playlistinfo = []  
      playlisttitle = []
      # pplaylist title and description
      for x in item:
        playlistinfo.append(x)
      playlisttitle.append(playlistinfo[0])
      str2 = ' - '.join(str(e) for e in playlistinfo)
      infoPerGm.append(str2)
      infoPerGm.append('Songs: Title - Artist - Length(s) - Explicit')
      for i in playlisttitle:
      # print pplaylist title and desc. along with headers for song details
        cmd3 = "SELECT s.title, a.name, s.song_length/1000 as length, s.explicit FROM songs AS s, artists AS a, PublicPlaylists_Generates AS p, records AS r WHERE p.title = :name3 and p.song_id = s.song_id and p.song_id = r.song_id and a.artist_id = r.artist_id"
        cursor3 = g.conn.execute(text(cmd3), :name3 = i)
        row = cursor3.fetchall()
        # each item is a tuple of title, name, song length, explicit
        for item in row:
          songinfo = []
          # this loop allows item3 to be made into an array
          for y in item:
            songinfo.append(y)
          str3 = ' - '.join(str(e) for e in songinfo)
          infoPerGm.append(str3)
        cursor3.close()
    cursor2.close()
    infoPerGm.append(' - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    
  context = dict(data = infoPerGm)
  
  return render_template("gandm.html", **context)

######################################## SEARCH METHODS ########################################
# userinput: publicplaylist_id ex. 0rk49r
@app.route('/lookup_playlist')
def songs_given_playlist_id():
  pp_id = request.form['publicplaylist_id']
  playlistinfo = []
  try:
    cmd = "SELECT P.title, P.description FROM publicplaylists_generates AS P WHERE P.publicplaylist_id = :pp_id"
    cursor = g.conn.execute(text(cmd), :pp_id = pp_id)
  except:
    return redirect('/invalid_action/')
  
  row = cursor.fetchall()
  cursor.close()
  # print gm title and description
  for item in row:
    ndinfo = []
    for x in item:
      ppinfo.append(x)
    str1 = ' - '.join(str(e) for e in ndinfo)
    playlistinfo.append(str1)
    playlistinfo.append('Songs: Title - Artist - Length(s) - Explicit')    
  try:
    cmd = "SELECT S.title, A.name, S.song_length/1000 as length, S.explicit FROM songs AS S, artists AS A, PublicPlaylists_Generates AS P, records AS R WHERE p.title = :title and P.song_id = S.song_id and P.song_id = R.song_id and A.artist_id = R.artist_id"
    cursor = g.conn.execute(text(cmd), :title = pp_id)
  except:
    return redirect('/invalid_action/')  
  row = cursor.fetchall()
    for item in row:
      songinfo = []
      for y in item:
            songinfo.append(y)
          str3 = ' - '.join(str(e) for e in songinfo)
          playlistinfo.append(str3)
        cursor.close()
        
  context = dict(data = playlistinfo)
  return render_template("lookup_playlist.html", **context)

######################################## INSERT METHODS ########################################
@app.route('/insert_new_song', methods=['POST'])
def insert_new_song():
  song_id = request.form['song_id']
  song_length = request.form['song_length']
  explicit = request.form['explicit']
  title = request.form['title']
  try:
    cmd = "INSERT INTO songs VALUES (DEFAULT, (:song_id), (:song_length), (:explicit), (:title))"
    g.conn.execute(text(cmd), :song_id = song_id, :song_length = song_length, :explicit = explicit, :title = title)
    return redirect('/')
  except:
    return redirect('/invalid_action/')

@app.route('/insert_new_personalplaylist', methods=['POST'])
def insert_new_personalplaylists_manages():
  user_id = request.form['user_id']
  title = request.form['title']
  date_created = request.form['date_created']
  song_id = request.form['song_id']
  try:
    cmd = "INSERT INTO personalplaylists_manages VALUES (DEFAULT, (:user_id), (:title), (:date_created), (:song_id))"
    g.conn.execute(text(cmd), :user_id = user_id, :title = title, :date_created = date_created, :song_id = song_id)
    return redirect('/')
  except:
    return redirect('/invalid_action/')

@app.route('/insert_new_publicplaylist', methods=['POST'])
def insert_new_publicplaylists_generates():
  user_id = request.form['user_id']
  publicplaylist_id = request.form['publicplaylist_id']
  title = request.form['title']
  description = request.form['description']
  song_id = request.form['song_id']
  try:
    cmd = "INSERT INTO personalplaylists_manages VALUES (DEFAULT, (:user_id), (:publicplaylist_id), (:title), (:description), (:song_id))"
    g.conn.execute(text(cmd), :user_id = user_id, :publicplaylist_id = publicplaylist_id, :title = title, :description = description, :song_id = song_id)
    return redirect('/')
  except:
    return redirect('/invalid_action/')

@app.route('/insert_new_artist', methods=['POST'])
def insert_new_artist():
  artist_id = request.form['artist_id']
  genre = request.form['genre']
  name = request.form['name']
  
  try:
    cmd = "INSERT INTO songs VALUES (DEFAULT, (:artist_id), (:genre), (:name))"
    g.conn.execute(text(cmd), :artist_id = artist_id, :genre = genre, :name = name)
    return redirect('/')
  except:
    return redirect('/invalid_action/')
     
@app.route('/insert_new_library', methods=['POST'])
def insert_library_adds():
  library_index = request.form['library_index']
  library_name = request.form['library_name']
  user_id = request.form['user_id']
  album_id = request.form['album_id']
  date_added = request.form['date_added']
  try:
    cmd = "INSERT INTO personalplaylists_manages VALUES (DEFAULT, (:library_index), (:library_name), (:user_id), (:album_id), (:date_added))"
    g.conn.execute(text(cmd), :library_index = library_index, :library_name = library_name, :user_id = user_id, :album_id = album_id, :date_added = date_added)
    return redirect('/')
  except:
    return redirect('/invalid_action/')

@app.route('/insert_new_artist', methods=['POST'])
def insert_new_artist():
  gm_id = request.form['gm_id']
  gm_name = request.form['gm_name']
  gm_description = request.form['gm_description']
  try:
    cmd = "INSERT INTO songs VALUES (DEFAULT, (:gm_id), (:gm_name), (:gm_description))"
    g.conn.execute(text(cmd), :gm_id = gm_id, :gm_name = gm_name, :gm_description = gm_description)
    return redirect('/')
  except:
    return redirect('/invalid_action/')   
   
@app.route('/insert_new_studio', methods=['POST'])
def insert_new_studio():
  studio_id = request.form['studio_id']
  name = request.form['name']
  location = request.form['location']
  try:
    cmd = "INSERT INTO songs VALUES (DEFAULT, (:studio_id), (:name), (:location))"
    g.conn.execute(text(cmd), :studio_id = studio_id, :name = name, :location = location)
    return redirect('/')
  except:
    return redirect('/invalid_action/')       
    

    
######################################## EXAMPLES ########################################
    
@app.route('/results', methods=['GET', 'POST'])
def results(name):
  #Search results here change this
  return render_template("gandm.html", **context)


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
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
