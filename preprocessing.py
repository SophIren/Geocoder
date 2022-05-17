import settings
import osmium as o
import DB
from table import Table


class AddressPreprocessor(o.SimpleHandler):
    def __init__(self, linked_nodes):
        super(AddressPreprocessor, self).__init__()
        self.geo_entries = []
        self.linked_nodes = linked_nodes

    def add_entry(self, obj, lat, lon):
        entry = (obj.id,
                 lat, lon,
                 obj.tags['addr:city'],
                 obj.tags['addr:street'],
                 obj.tags['addr:housenumber'],
                 obj.tags.get('addr:postcode'))
        self.geo_entries.append(entry)

    def node(self, n):
        self.add_entry(n, n.location.lat, n.location.lon)

    def way(self, w):
        self.add_entry(w, *self.get_avg_coordinate(w))

    def get_avg_coordinate(self, way):
        sum_lat = 0
        sum_lon = 0
        n = 0
        for node in way.nodes:
            location = self.linked_nodes[node.ref]
            sum_lat += location[0]
            sum_lon += location[1]
            n += 1
        return sum_lat / n, sum_lon / n


class LinkedNodesPreprocessor(o.SimpleHandler):
    def __init__(self):
        super(LinkedNodesPreprocessor, self).__init__()
        self.nodes = {}

    def node(self, n):
        self.nodes[n.id] = (n.location.lat, n.location.lon)


def link_nodes(linked_nodes_data_path: str):
    linked_nodes_handler = LinkedNodesPreprocessor()
    linked_nodes_handler.apply_file(linked_nodes_data_path)
    return linked_nodes_handler


def prepare_addresses(addresses_data_path, linked_nodes):
    address_handler = AddressPreprocessor(linked_nodes)
    address_handler.apply_file(addresses_data_path)
    return address_handler


def fill_secondary_table(db: DB.DataBase, take_from_col: str,
                         save_to_table: Table):
    distinct = db.get_entries_by_column(settings.GEO_TABLE,
                                        take_from_col, distinct=True)
    entries = [(str(i + 1), distinct[i][0]) for i in
               range(len(distinct))]
    db.add_entries(save_to_table, entries)


def main():
    print('LINKING NODES')
    linked_nodes_handler = link_nodes(settings.LINKED_NODES_DATA_PATH)

    print('PREPPING ADDRESSES')
    address_handler = prepare_addresses(settings.ADDRESSES_DATA_PATH,
                                        linked_nodes_handler.nodes)

    print('ADDING ENTRIES')
    db = DB.DataBase([settings.GEO_TABLE, settings.CITY_TABLE,
                      settings.STREET_TABLE])
    db.add_entries(settings.GEO_TABLE, address_handler.geo_entries)
    fill_secondary_table(db, settings.GEO_PARAM_NAMES.city, settings.CITY_TABLE)
    fill_secondary_table(db, settings.GEO_PARAM_NAMES.street,
                         settings.STREET_TABLE)


if __name__ == '__main__':
    main()
