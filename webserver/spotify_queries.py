#!/usr/bin/env python2.7

"""
SQL Queries to be used by our spotify app
"""

#cmd1 in gandm
GM_DETAILS_BY_GM_ID = (
  "SELECT G.gm_name, G.gm_description "
  "FROM genresmoods AS G "
  "WHERE G.gm_id = (:gm_id)"
)

