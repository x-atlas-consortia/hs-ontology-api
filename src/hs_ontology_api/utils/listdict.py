# coding: utf-8

def remove_duplicate_dicts_from_list(listinput: list[dict], indexval: str) -> list[dict]:
    """
    Removes duplicate dictionaries from a list of dictionaries.
    Assumes that each dictionary has a key with values that can be treated as an index.

    :param dictinput: list of dictionaries with duplicates--e.g., [{"a":"1"},{"b":"2"},{"a":"1}]
    :param indexkey: name of the unique --e.g., "a"
    :return: a list of dictionaries without duplicates--e.g., [{"a":"1"},{"b":"2"}]

    """

    listunique = {}
    listcheck = listinput
    index = 0
    while index < len(listcheck):
        if listcheck[index]['name'] in listunique:
            del listcheck[index]
        else:
            listunique[listcheck[index]['name']] = 1
            index += 1

    return listcheck