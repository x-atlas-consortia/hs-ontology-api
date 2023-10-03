# coding: utf-8

# JAS September 2023

# Utilities to load large Cypher query strings.

import os

def loadquerystring(filename: str) ->str:

    # Load a query string from a file.
    # filename: filename, without path.

    # Assumes that the file is in the cypher directory.

    fpath = os.path.dirname(os.getcwd())
    fpath = os.path.join(fpath,'src/hs_ontology_api/cypher',filename)

    f = open(fpath, "r")
    query = f.read()
    f.close()
    return query
