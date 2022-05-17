import settings
import osmium as o
import DB


class AddressPreprocessor(o.SimpleHandler):
    def __init__(self, linked_nodes):
        super(AddressPreprocessor, self).__init__()
        self.entries = []
        self.cities = set()
        self.streets = set()
        self.linked_nodes = linked_nodes

    def add_entry(self, obj, lat, lon):
        entry = (obj.id,
                 lat, lon,
                 obj.tags['addr:city'],
                 obj.tags['addr:street'],
                 obj.tags['addr:housenumber'],
                 obj.tags.get('addr:postcode'))
        self.entries.append(entry)
        self.cities.add(obj.tags['addr:city'])
        self.streets.add(obj.tags['addr:street'])

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


def create_tables(entries):
    db = DB.DataBase([settings.GEO_TABLE])
    db.add_entries(settings.GEO_TABLE, entries)

    db.close()


def main():
    print('LINKING NODES')
    linked_nodes_handler = link_nodes(settings.LINKED_NODES_DATA_PATH)

    print('PREPPING ADDRESSES')
    address_handler = prepare_addresses(settings.ADDRESSES_DATA_PATH,
                                        linked_nodes_handler.nodes)

    print('ADDING ENTRIES')
    create_geo_table(address_handler.entries)


if __name__ == '__main__':
    main()
