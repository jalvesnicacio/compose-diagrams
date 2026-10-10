from .service_builder import ServiceBuilder
from .diagram import Diagram

class DiagramBuilder():

    def __init__(self, data):
        self.__data = data
        self.__title = None
        self.__services = []
        self.__volumes = []
        self.__networks = []

    def with_title(self):
        services = self.__data.get('services')
        title = ""
        for key in services:
            title = title + key + " "
        self.__title = title
        return self

    def with_services(self):
        data_services = self.__data.get('services')
        for key in data_services:
            dict_service = data_services[key]
            service = (
                ServiceBuilder(key, dict_service)
                .with_image_name()
                .with_container_name()
                .with_volumes()
                .with_depends_on()
                .with_links()
                .build()
            )
            self.__services.append(service)
        return self

    def with_volumes(self):
        data_volumes = self.__data.get('volumes')
        if(data_volumes is not None):
            for v in data_volumes:
                self.__volumes.append(v)
        return self

    def with_networks(self):
        data_networks = self.__data.get('networks')
        if(data_networks is not None):
            for n in data_networks:
                self.__networks.append(n)
        return self

    def build(self):
        return Diagram(
            self.__title,
            self.__services,
            self.__volumes,
            self.__networks
        )
