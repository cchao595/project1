<html>
  <style>
    body{ 
      font-size: 15pt;
      font-family: arial;
    }
  </style>


<body>
  <h1>Welcome to Spotify!</h1>
  <h2>About</h2>
  <div>This is where users can find out the top hits other people are listening to, which artists are the hottest, and the latest releases. Each user can create playlists of songs,libraries of albums, and follow artists. Click on user profiles to find out more about our users. Click on artist profiles to find all the albums and songs released by each artist.</div>


  <div>Our top 5 Artists:</div>

  <ol>
    {% for n in data %}
    <li>{{n}}</li>
    {% endfor %}
  </ol>

  <div>Our top 5 Songs:</div>

  <ol>
    {% for n in data1 %}
    <li>{{n}}</li>
    {% endfor %}
  </ol>

  <div>New Albums:</div>

  <ol>
    {% for n in data2 %}
    <li>{{n}}</li>
    {% endfor %}
  </ol>

<p><a href="/userprofiles">User Profiles</a></p>
<p><a href="/artists">Artist Profiles</a></p>
<p><a href="/gandm">Genres and Moods</a></p>

<form method="GET" action="/search">
<p>Search for a song: <input type="text" name="name"> <input type="submit" value="Search"></p>
</form>

</body>


</html>
