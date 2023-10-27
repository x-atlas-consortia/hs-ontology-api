# Cypher query strings

## Background
The usual form of development for an endpoint in hs-ontology-api involves:
1. Developing a Cypher query against the UBKG neo4j instance, using the neo4j browser.
2. Exporting the Cypher query as a string.
3. Incorporating the Cypher query string into a function in the script **neo4j_logic.py**.

Cypher queries against the UBKG can be complex, and require extensive knowledge of the UBKG model. 
The task to develop Cypher queries can be separated by role from the task of deliverying query results to a response, or return from an endpoint.

To facilitate development, Cypher query strings should be kept separate from endpoint function code.

## Solution Architecture

1. The _cypher_ directory contains Cypher queries in text files with extension .cypher.
2. The queries can be annotated using Cypher commenting (i.e., using "/").
3. Queries can be parameterized for use with endpoint code by using variables with the $prefix--e.g.,
```
// The calling function in neo4j_logic.py will replace $ids.
WITH [$ids] AS ids
```
4. Functions in **neo4j_logic.py** can use the *loadquerystring* function in the **util_query.py** script to load a query string.

For example, the following code loads a query and then supplies parameters:
```
    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'genedetail.cypher'
    query = loadquerystring(queryfile)

    # Incorporate ids from request body into parameterized Cypher query string.
    ids: str = ', '.join("'{0}'".format(i) for i in gene_ids['ids'])
    query = query.replace('$ids', ids)

```