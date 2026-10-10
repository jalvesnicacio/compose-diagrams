# DAD - Descriptor to Architectural Diagrams
Create system architectural diagrams from docker-compose files.

In its current version, DAD is a **prototype**.
Its goal is to design architecture diagrams of distributed systems from  docker-compose files.

DAD reads multi-container [Docker Compose](https://docs.docker.com/compose/) `.yaml` files and outputs a diagram `.png` image representing the Docker Compose file.
  
```
  ┌────────────────────┐       ┌────────────────────┐
  │ Docker Compose     │       │ Diagram .png image │
  │ .yalm file         │       │                    │
  │────────────────────│       │            ┌───┐   │
  │ version: 'x.y'     │       │  ┌───┐ --- │   │   │
  │ services:          │  ══>  │  │   │     └───┘   │
  │   service X:       │       │  └───┘ \           │
  │     params...      │       │         \ ┌───┐    │
  │   service Y:       │       │           │   │    │
  │ ...                │       │           └───┘    │
  └────────────────────┘       └────────────────────┘
```

## Setting up

DAD needs [Python 3](https://www.python.org/) >= 3.9 and [Graphviz](https://graphviz.org/download/) (the `dot` command) installed.

Then, from the project folder:
```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install .
```

This also installs [Diagram as Code](https://diagrams.mingrammer.com/) and [PyYAML](https://pyyaml.org/).

## Running

```
$ descriptors-diagrams docker-compose.yaml
```

DAD reads the Docker Compose file and writes `docker-compose.png` in the current folder. Some options:

```
$ descriptors-diagrams docker-compose.yaml -o output/my-system.svg   # output path and format
$ descriptors-diagrams docker-compose.yaml -d LR                     # left-to-right layout
$ descriptors-diagrams docker-compose.yaml --script                  # also print the Diagram as Code script
$ descriptors-diagrams --help
```

Supported formats are `png`, `svg`, `pdf` and `jpg`. Sample input files are in the `docker-compose-files` folder.

## Example

### Input

A Docker Compose `.yalm` file.

```
version: '3.8'
services:
  mysql:
    image: mysql
    ports:
     - 3306:3306
    environment:
     - MYSQL_ROOT_PASSWORD=secret
     - MYSQL_USER=mysqluser
     - MYSQL_PASSWORD=mysqlpw
    volumes:
      - db-data:/var/lib/mysql
  postgres:
    image: postgres:9.4
    volumes:
      - db-data:/var/lib/postgresql/data
  dblog:
    build:
      context: api
      dockerfile: Dockerfile
      container_name: dblog
    restart: always
    ports:
      - "9001:9001"
    depends_on:
      - mysql
      - postgres
    links:
      - zookeeper
  zookeeper:
    image: debezium/zookeeper:${DEBEZIUM_VERSION}
    ports:
     - 2181:2181
     - 2888:2888
     - 3888:3888
  kafka:
    build:
      context: kafka
      dockerfile: Dockerfile
      container_name: kafka
    links:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: $CF_HOST_IP
      KAFKA_ZOOKEEPER_CONNECT: zk:2181
      KAFKA_MESSAGE_MAX_BYTES: 2000000
      KAFKA_CREATE_TOPICS: "Topic1:1:1"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - zookeeper
volumes:
  db-data:
```

### Output

A `.png` image file.

![Diagram example: currently compose-diagrams recognizes the services declared in the docker-compose](github-assets/diagram.png)



