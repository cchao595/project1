#!/usr/bin/env python2.7

"""
SQL Queries to be used by our spotify app
"""

#cmd in artist
USER_DETAILS_BY_user_id = (
  "SELECT U.username, U.dob, U.email "
  "FROM GeneralUsers AS G, Users AS U "
  "WHERE U.user_id = :user_id"
)

#cmd2 in artist
PP_TITLES_BY_user_id = (
  "SELECT DISTINCT P.title "
  "FROM PersonalPlaylists_manages AS P "
  "WHERE P.user_id = (:user_id)"
)

#cmd3 in artist
LIST_ARTISTS_user_id = (
  "SELECT DISTINCT A.name "
  "FROM Follows AS F, Artists AS A "
  "WHERE A.artist_id = F.artist_id AND F.user_id = (:user_id)"
)

#cmd0 in artist
LIBRARY_DETAILS_inputuid = (
  "SELECT DISTINCT L.library_index, L.library_name "
  "FROM Albums AS A, library_adds AS L "
  "WHERE L.album_id = album_id AND L.user_id = (:user_id)"
)

#cmd1 in gandm
GM_DETAILS_BY_gm_id = (
  "SELECT G.gm_name, G.gm_description "
  "FROM genresmoods AS G "
  "WHERE G.gm_id = (:gm_id)"
)

#cmd2 in gandm
PP_DETAILS_BY_gm_id = (
  "SELECT DISTINCT P.title, P.description "
  "FROM publicplaylists_generates AS P, gather AS G "
  "WHERE G.publicplaylist_id = P.publicplaylist_id AND G.gm_id = (:gm_id)"
)

#cmd3 in gandm
SONG_DETAILS_BY_title = (
  "SELECT S.title, A.name, S.song_length/1000 as length, S.explicit "
  "FROM songs AS S, artists AS A, PublicPlaylists_Generates AS P, records AS R "
  "WHERE P.song_id = S.song_id and P.song_id = R.song_id and A.artist_id = R.artist_id AND P.title = (:title)"
)


