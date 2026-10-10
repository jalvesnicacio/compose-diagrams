from .service import Service

class ServiceBuilder():
    def __init__(self, name, dict):
        self.__name = name
        self.__dict = dict
        self.__image_name = None
        self.__container_name = None
        self.__volumes = []  #List of volumes
        self.__depends_on = [] #Service depends on other services
        self.__links = [] #List of links
        self.__ports = [] #Published ports

    def with_image_name(self):
        dict = self.__dict
        if(dict.get('image') is not None):
            self.__image_name = self.set_image_name(dict.get('image'))
        elif(dict.get('build') is not None):
            build = dict.get('build')
            if not isinstance(build,str):
                if(build.get('container_name') is not None):
                    self.__image_name = build.get('container_name')
            else:
                self.__image_name = build
        return self

    def with_container_name(self):
        dict = self.__dict
        if(dict.get('container_name') is not None):
            self.__container_name = dict.get('container_name')
        elif(dict.get('build') is not None):
            build = dict.get('build')
            if not isinstance(build, str):
                if(build.get('container_name') is not None):
                    self.__container_name = build.get('container_name')
            else:
                self.__container_name = build
        return self

    def with_ports(self):
        data_ports = self.__dict.get('ports')
        if(data_ports is not None):
            for p in data_ports:
                if(isinstance(p, dict)):
                    #long syntax: {target: 80, published: 8080}
                    port = str(p.get('target'))
                    if(p.get('published') is not None):
                        port = str(p.get('published')) + ":" + port
                else:
                    port = str(p)
                self.__ports.append(port)
        return self

    def with_links(self):
        data_links = self.__dict.get('links')
        if(data_links is not None):
            for link in data_links:
                self.__links.append(link)
        return self

    # Todo: is not finished
    def with_volumes(self):
        data_volumes = self.__dict.get('volumes')
        if(data_volumes is not None):
            for v in data_volumes:
                if(type(v) is str):
                    volume = v.split(":")[0]
                else:
                    volume = v.get('source')
                self.__volumes.append(volume)
        return self

    # Todo: is not finished
    def with_depends_on(self):
        data_depends_on = self.__dict.get('depends_on')
        if(data_depends_on is not None):
            for don in data_depends_on:
                self.__depends_on.append(don)
        return self


    def set_image_name(self, raw_name):
        name = raw_name
        if name.find("/"):
            arr_name = name.split("/")
            name = arr_name[len(arr_name) - 1]
        if name.find(":"):
            arr_name = name.split(":")
            name = arr_name[0]
        return name


    def build(self):
        # services without a recognizable image fall back to the service name
        return Service(
            self.__name,
            self.__image_name or self.__name,
            self.__container_name,
            self.__volumes,
            self.__depends_on,
            self.__links,
            self.image(),
            self.build_context(),
            self.__ports)

    def image(self):
        image = self.__dict.get('image')
        return str(image) if image is not None else None

    def build_context(self):
        build = self.__dict.get('build')
        if isinstance(build, dict):
            build = build.get('context')
        return str(build) if build is not None else None
