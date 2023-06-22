import logging
import neo4j

logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

instance = None

class Neo4jManager(object):
    @staticmethod
    def create(server, username, password):
        if instance is not None:
            raise Exception(
                "An instance of Neo4jManager exists already. Use the Neo4jManager.instance() method to retrieve it.")

        return Neo4jManager(server, username, password)

    @staticmethod
    def instance():
        if instance is None:
            raise Exception(
                "An instance of Neo4jManager does not yet exist. Use Neo4jManager.create() to create a new instance")

        return instance

    @staticmethod
    def is_initialized():
        return instance is not None

    def __init__(self, server, username, password):
        global instance
        self.driver = neo4j.GraphDatabase.driver(server, auth=(username, password))
        if instance is None:
            instance = self


    def relationships_for_gene_target_symbol_get(self, target_symbol: str) -> dict:
        """
        Provide: Relationships for the gene target_symbol.

        The target_symbol can be a name, symbol, alias, or prior symbol,
        You will get this information on the matched gene if it exists:
        Approved Symbol(s), Previous Symbols, and Alias Symbols.
        You will get back 'None' if none of this information is found on the target_symbol.

        In theory there should be only one Approved Symbol, and Previous Symbol,
        but all types are returned as arrays just in case.

        Also, other relationships may exist but only those mentioned will be returned.
        """
        query: str = "CALL {" \
                     "MATCH (tSearch:Term)<-[rSearch]-(cSearch:Code)<-[:CODE]-(pSearch:Concept) " \
                     f"WHERE toUpper(tSearch.name)='{target_symbol.upper()}' AND " \
                     "cSearch.SAB='HGNC' AND " \
                     "rSearch.CUI=pSearch.CUI " \
                     "RETURN DISTINCT cSearch.CodeID AS HGNCCodeID" \
                     "} " \
                     "WITH HGNCCodeID " \
                     "MATCH (pHGNC:Concept)-[:CODE]->(cHGNC:Code)-[r]-(tHGNC:Term) " \
                     "WHERE cHGNC.CodeID=HGNCCodeID AND " \
                     "r.CUI=pHGNC.CUI AND " \
                     "type(r) IN ['ACR','NS','SYN','PT'] " \
                     "RETURN cHGNC.CODE AS code, " \
                     "CASE type(r) " \
                     "WHEN 'ACR' THEN 'symbol-approved' " \
                     "WHEN 'NS' THEN 'symbol-previous' " \
                     "WHEN 'SYN' THEN 'symbol-alias' " \
                     "WHEN 'PT' THEN 'name-approved' " \
                     "ELSE type(r) " \
                     "END AS type, " \
                     "tHGNC.name AS value " \
                     "order by type(r)"
        result: dict = {
            'symbol-approved': [],
            'symbol-previous': [],
            'symbol-alias': []
        }
        with self.driver.session() as session:
            recs: neo4j.Result = session.run(query)
            if recs.peek() is None:
                return None
            for rec in recs:
                try:
                    type_name: str = rec['type']
                    value: str = rec['value']
                    if type_name == 'symbol-approved' or \
                            type_name == 'symbol-previous' or \
                            type_name == 'symbol-alias':
                        result[type_name].append(value)
                except KeyError:
                    pass
        return result
