from diagrams import Cluster, Diagram as DaC, Edge
from diagrams.onprem.compute import Server
from diagrams.c4 import Container, Database

#images that hold data are drawn as a C4 database
DATA_STORES = ("postgres", "postgis", "mysql", "mariadb", "mongo", "redis", "memcached", "cassandra",
    "elasticsearch", "opensearch", "influxdb", "couchdb", "neo4j", "clickhouse", "mssql", "cockroach")

class Service():

    def __init__(self, service_name, image_name, container_name, volumes, depends_on, links, image=None, build=None, ports=()):
        self.__service_name = service_name
        self.__image_name = image_name
        self.__container_name = container_name
        self.__volumes = volumes
        self.__depends_on = depends_on
        self.__links = links
        self.__image = image
        self.__build = build
        self.__ports = ports
        #self.node = service_name

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    @property
    def service_name(self):
        return self.__service_name

    @property
    def image_name(self):
        return self.__image_name

    @property
    def depends_on(self):
        return self.__depends_on

    @property
    def links(self):
        return self.__links

    @property
    def volumes(self):
        return self.__volumes

    def design(self):
        s = "    with Cluster(\"" + self.__service_name + " service\"):" + '\n'
        with Cluster(self.__service_name + " service"):
            s = s + "\t\t" + self.__image_name + " = Server(\""+ self.__image_name + "\")\n"
            img = Server(self.__image_name)
            self.node = img
        return s

    @property
    def variable(self):
        #name of this service in the generated script
        return "".join(c if c.isalnum() else "_" for c in self.__service_name)

    @property
    def technology(self):
        if self.__image is not None:
            return self.__image
        if self.__build is not None:
            return "build: " + self.__build
        return ""

    @property
    def is_data_store(self):
        return any(name in self.__image_name.lower() for name in DATA_STORES)

    def design_c4(self):
        description = ""
        if self.__ports:
            description = "Ports: " + ", ".join(self.__ports)
        kind = Database if self.is_data_store else Container
        #the C4 boxes have a fixed size: widen them when the image name is long
        attrs = {}
        width = 0.07 * len("[" + kind.__name__ + ": " + self.technology + "]") + 0.3
        if width > (2.6 if description else 2):
            attrs["width"] = str(round(width, 1))
        self.node = kind(self.__service_name, self.technology, description, **attrs)
        extra = "".join(", " + k + "=" + repr(v) for k, v in attrs.items())
        return "        " + self.variable + " = " + kind.__name__ + "(" + repr(self.__service_name) + ", " + repr(self.technology) + ", " + repr(description) + extra + ")\n"

    @property
    def node(self):
        return self.__node

    @node.setter
    def node(self, img):
        self.__node = img
