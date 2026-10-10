from diagrams import Cluster, Diagram as DaC, Edge
from diagrams.onprem.compute import Server

class Service():

    def __init__(self, service_name, image_name, container_name, volumes, depends_on, links):
        self.__service_name = service_name
        self.__image_name = image_name
        self.__container_name = container_name
        self.__volumes = volumes
        self.__depends_on = depends_on
        self.__links = links
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
    def node(self):
        return self.__node

    @node.setter
    def node(self, img):
        self.__node = img
