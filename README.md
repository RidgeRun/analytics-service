## RidgeRun Analytics Microservice 1.0.0


Analytics Microservice reads the detection metadata from redis and executes the enabled actions.
The actions can be: move the camera to the detected object position in PTZ microservice
and start an event recording in VST microservice.

By default all the actions are disabled, you need to enable them through a configuration file or
the server with the [configuration request](api/openapi.yaml).
In both cases, the configuration is defined in JSON format as follows:

```bash
{
  "move_camera": {
    "enable": 1,
    "port": 5030,
    "ip": "127.0.0.1"
  },
  "record": {
    "enable": 0,
    "port": 81,
    "ip": "127.0.0.1"
  }
}
```
As you can see the configuration allows you to enable/disable each of the available actions
and configure the URI of the corresponding microservice.

### Running the service

The project is configured (via setup.py) to install the service with the name __analytics__. So to install it run:

```bash
pip install .
```

Then you will have the service with the following options:

```bash
usage: analytics [-h] [--port PORT] [--host HOST] [--config-file CONFIG_FILE]

options:
  -h, --help            show this help message and exit
  --port PORT           Port for server
  --host HOST           Server ip address
  --config-file CONFIG_FILE
                        Configuration JSON file
```


To start the service in address 127.0.0.1 and port 5040 just run:
```bash
analytics
```

If you want to serve in a different port or address, use the __--port__ and __--host__ options.


## Analytics Docker


### Build the container

You can build the analytics microservice container using the Dockerfile in the docker directory.
This includes a base LT4 image and the dependencies to run the analytics microservice application.

First, we need to prepare a context directory for this build, you need to create a directory
and include this repository and the rrms-utils project. The Dockerfile will look for both packages
in the context directory and will copy them to the container.

```bash
analytics-context/
├── analytics
└── rrms-utils
```

Then build the container image with the following command:

```bash
DOCKER_BUILDKIT=0 docker build --network=host --tag ridgerun/analytics-service --file analytics-context/analytics/docker/Dockerfile analytics-context/
```

Change analytics-context/ to your context's path and the tag to the name you want to give to the image.

### Launch the container

The container can be launched by running the following command:

```bash
docker run --runtime nvidia -it --network host --volume /home/nvidia/analytics-configs/:/configs --name analytics-service  ridgerun/analytics-service:latest analytics --host 0.0.0.0 --config-file /configs/analytics.json
```

Here we are creating a container called analytics-service that will start the analytics application,
launching the server allowing access to any IP available in the device. Also provides a configuration file through the configs volume.
