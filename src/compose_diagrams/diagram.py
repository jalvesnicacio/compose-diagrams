from diagrams import Cluster, Diagram as DaC, Edge
from .service import Service
from diagrams.k8s.storage import Volume
from diagrams.c4 import Database, Relationship, SystemBoundary

# from diagrams import Cluster, Diagram, Edge
# from diagrams.onprem.compute import Server


class Diagram():
    def __init__(self, title, services, volumes, networks, name=None):
        self.__title = title
        #name of the compose project, when the file declares one
        self.__name = str(name) if name else "Docker Compose"
        self.__services = services
        self.__volumes = volumes
        self.__networks = networks
        self.__dependencies = self.map_dependencies()
        self.__links = self.map_links()

    @property
    def services(self):
        return self.__services

    def service_by_name(self, name):
        for s in self.__services:
            if(s.service_name == name):
                return s
        return None

    def design(self, diagram_filename, outformat="png", direction="TB", style="ad-hoc"):
        if style == "c4":
            return self.design_c4(diagram_filename, outformat, direction)
        #dac is the script for Diagram tool:

        dac = "from diagrams import Cluster, Diagram as DaC, Edge\nfrom service import Service\nfrom diagrams.k8s.storage import Volume\nfrom diagrams.onprem.compute import Server\n\n"
        dac = dac + "with DaC(\"" + self.__title + "\", filename= \"./diagram-adhoc\", show=False, direction=\"" + direction + "\"):" + '\n'
        with DaC(self.__title, filename= diagram_filename, outformat=outformat, show=False, direction=direction):
            for s in self.__services:
                dac = dac + s.design()
            dac = dac + self.design_edges()
            dac = dac + self.design_volumes()
        return dac


    #C4 container diagram: services are containers (or databases) inside
    #the system boundary; named volumes are databases the services store data in
    def design_c4(self, diagram_filename, outformat, direction):
        dac = "from diagrams import Diagram\nfrom diagrams.c4 import Container, Database, Relationship, SystemBoundary\n\n"
        dac = dac + "with Diagram(" + repr(self.__name) + ", filename=\"./diagram-c4\", show=False, direction=\"" + direction + "\", graph_attr={\"splines\": \"spline\"}):" + '\n'
        dac = dac + "    with SystemBoundary(" + repr(self.__name) + "):" + '\n'
        with DaC(self.__name, filename= diagram_filename, outformat=outformat, show=False, direction=direction, graph_attr={"splines": "spline"}):
            volume_nodes = {}
            with SystemBoundary(self.__name):
                for s in self.__services:
                    dac = dac + s.design_c4()
                for s in self.__services:
                    for v in s.volumes:
                        #bind mounts (host paths) are not part of the system
                        if v in self.__volumes and v not in volume_nodes:
                            volume_nodes[v] = Database(v, "Docker volume")
                            dac = dac + "        " + self.volume_variable(v) + " = Database(" + repr(v) + ", \"Docker volume\")\n"
            for dep in self.__dependencies:
                self.service_by_name(dep[0]).node >> Relationship("depends on") >> self.service_by_name(dep[1]).node
                dac = dac + "    " + self.service_by_name(dep[0]).variable + " >> Relationship(\"depends on\") >> " + self.service_by_name(dep[1]).variable + "\n"
            for link in self.__links:
                self.service_by_name(link[0]).node >> Relationship("links to") >> self.service_by_name(link[1]).node
                dac = dac + "    " + self.service_by_name(link[0]).variable + " >> Relationship(\"links to\") >> " + self.service_by_name(link[1]).variable + "\n"
            for s in self.__services:
                for v in s.volumes:
                    if v in volume_nodes:
                        s.node >> Relationship("stores data in") >> volume_nodes[v]
                        dac = dac + "    " + s.variable + " >> Relationship(\"stores data in\") >> " + self.volume_variable(v) + "\n"
        return dac

    def volume_variable(self, volume):
        return "vol_" + "".join(c if c.isalnum() else "_" for c in volume)

    def map_dependencies(self):
        dependencies_list = []
        for s in self.__services:
            for don in s.depends_on:
                if self.service_by_name(don) is not None:
                    dependencies_list.append((s.service_name,don))
        return dependencies_list

    def map_links(self):
        links_list = []
        for s in self.__services:
            for link in s.links:
                #links can be declared as "service:alias"
                link = link.split(":")[0]
                if self.service_by_name(link) is not None:
                    links_list.append((s.service_name,link))
        return links_list

    #criando as ligações entre os serviços, dependendo da relação
    # de dependência entre eles: srv1 >> srv2
    def design_edges(self):
        e = ""
        for dep in self.__dependencies:
             node0 = self.service_by_name(dep[0]).node
             node1 = self.service_by_name(dep[1]).node
             node0 >> node1
             #dep[] keep de service names
             e = e + "    " + self.service_by_name(dep[0]).image_name + " >> " + self.service_by_name(dep[1]).image_name + "\n"
        for link in self.__links:
            node0 = self.service_by_name(link[0]).node
            node1 = self.service_by_name(link[1]).node
            node0 - node1
            #link[] keep the services names
            e = e + "    " + self.service_by_name(link[0]).image_name + " - " + self.service_by_name(link[1]).image_name + "\n"
        return e
        #examples:
        # self.service_by_name('api').node << self.service_by_name('web').node
        # self.service_by_name('web').node >> self.service_by_name('db').node
        # self.service_by_name('api').node >> self.service_by_name('db').node

    def design_volumes(self):
        services_volumes = []
        dashed_edge = Edge(color="darkgreen", style="dashed")
        dac_vol = ""
        volume_nodes = {}
        for s in self.__services:
            for v in s.volumes:
                #vol = v.split(":")
                services_volumes.append((s.service_name,v))
        for sv in services_volumes:
             if sv[1] not in volume_nodes:
                 volume_nodes[sv[1]] = Volume(sv[1])

                 #Generate script Diagram As Code:
                 vol_name = self.volume_variable(sv[1])
                 dac_vol = dac_vol + "    " + vol_name + " = Volume(\"" + sv[1] + "\")\n"
             vol_name = self.volume_variable(sv[1])
             volume_nodes[sv[1]] >> dashed_edge << self.service_by_name(sv[0]).node
             dac_vol = dac_vol + "    " + vol_name + " >> " + "Edge(color=\"darkgreen\", style=\"dashed\")" + " << " + self.service_by_name(sv[0]).image_name + "\n"
        return dac_vol
