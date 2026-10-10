from diagrams import Cluster, Diagram as DaC, Edge
from .service import Service
from diagrams.k8s.storage import Volume

# from diagrams import Cluster, Diagram, Edge
# from diagrams.onprem.compute import Server


class Diagram():
    def __init__(self, title, services, volumes, networks):
        self.__title = title
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

    def design(self, diagram_filename, outformat="png", direction="TB"):
        #dac is the script for Diagram tool:

        dac = "from diagrams import Cluster, Diagram as DaC, Edge\nfrom service import Service\nfrom diagrams.k8s.storage import Volume\nfrom diagrams.onprem.compute import Server\n\n"
        dac = dac + "with DaC(\"" + self.__title + "\", filename= \"./diagram-adhoc\", show=False, direction=\"" + direction + "\"):" + '\n'
        with DaC(self.__title, filename= diagram_filename, outformat=outformat, show=False, direction=direction):
            for s in self.__services:
                dac = dac + s.design()
            dac = dac + self.design_edges()
            dac = dac + self.design_volumes()
        return dac


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
        for s in self.__services:
            for v in s.volumes:
                #vol = v.split(":")
                services_volumes.append((s.service_name,v))
        for sv in services_volumes:
             vol = Volume(sv[1])
             vol >> dashed_edge << self.service_by_name(sv[0]).node

             #Generate script Diagram As Code:
             vol_name = "vol_" + self.service_by_name(sv[0]).image_name
             dac_vol = dac_vol + "    " + vol_name + " = Volume(\"" + sv[1] + "\")\n"
             dac_vol = dac_vol + "    " + vol_name + " >> " + "Edge(color=\"darkgreen\", style=\"dashed\")" + " << " + self.service_by_name(sv[0]).image_name + "\n"
        return dac_vol
