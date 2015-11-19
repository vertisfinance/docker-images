# docker-images
Some useful Docker images used by Vertis.

## Concepts
All images are created from our ```vertisfinance/base``` image. See details below.

### Minimal Image Size
This is a common goal image developers should take care of. There are some standard techniques and best practices to follow. Note that we do not go to extremes here: starting from ```debian``` seems to be OK for us.

### Configuration
Configuring your container should be easy and straightforward.
This is not easy to do right: There are too many places where one can put the same config value. Even worse, sometimes you need to put the same value in multiple places.

In our setup, configuration can go to:
- the ```Dockerfile```
- ```docker-compose.yml```
- the config file of your container's service (```pg_hba.conf```, ```nginx.conf```, etc.)
- ```run.py``` - see below

To make life a little easier, we need extensive documentation and some conventions to help design decisions. Some of these conventions are:
- The compose file is the best place for configuration
- Service config files should be placed to ```/opt/config``` and copied to an other location during startup. When a config value is given in an environment variable and need to be referenced in a ```.conf``` file, use variable substitution.
- Do reasonable checking at startup time.

### Variable Substitution
Example syntax (in an imaginary ```whatever.conf``` file):
```
logging: file
log_path: {{LOG_PATH}}
```
In the above case ```LOG_PATH``` must be given as an environment variable. During container startup this will be substituted and the file will be copied to an other location.

### run.py
All images have an entrypoint set to ```['python3', '/opt/config/run.py']```. This file uses python 3 (as you may have guessed) and the great [click](http://click.pocoo.org/5/) package to create commands. If you want to customize your container behavior, you will need to have a look at this file sooner or later.
This file imports from the ```runutils``` package which is installed by the base image and contains some utility functions to make writing common startup tasks (check for directory existence, creating users, groups, substitute variables in config files, run background services, etc.) easier.

With docker 1.9 one can set ```STOPSIGNAL``` to tell the docker daemon what signal to send to the container on stop, but in older versions this signal was always ```SIGTERM```. Originally ```run.py``` was written to catch this and send the proper signal to the main service.

### User, group IDs
We do not hard code ```uid``` and ```gid``` in the image. Whoever runs the container, she must be able to set the user and group ids of container processes. At some point in the future docker will be able to handle user namespaces, until then we must be able to provide this feature as a handmade solution.

### Semaphores
In some situations it is important for a container to start its service only after some other services are available. Starting the container's service is managed by ```runutils.run_daemon```. It is documented in ```runutils.py```, here we will look at only three arguments: ```waitfunc``` and ```initfunc``` are functions, ```semaphore``` is a file name given as an absolute path. Here is what the ```run_daemon``` function does:
- ```waitfunc``` is called. This function should not return until it is safe to run the service, i.e. dependent services are ready.
- ```initfunc``` is called. It is a good place to do some checks, prepare users, directories, etc. (In fact, directory creation can simply go to ```run.py``` into function ```run```. ```initfunc``` is useful when it uses dependent services: ```waitfunc``` makes sure they are usable.)
- The main service is started in a subprocess.
- The file at path given by ```semaphore``` is created.
- When the subprocess exits, the semaphore is deleted.

To summarize: provide a semaphore in service ```a``` and check for the existence of the semaphore in service ```b```.

## Images
The general structure of an image directory is this:
```
imagedir
  ├- config
  |   ├- run.py
  |   └- ..
  ├- context
  |   ├- Dockerfile
  |   └- ...
  └- docker-compose.yml
```
```context``` is obviously the docker build context, ```config``` is the directory which can be accessed by the container under ```/opt/config/```. This can be done by copying in the Dockerfile, volume binding or even copying directly to an existing container.

### vertisfinance/base
A lightweight base image for all subsequent images.

#### Environment variables
- ```USER_NAME```: optional. The name of the user to be created during startup.
- ```USER_UID```: optional, but required if ```USER_NAME``` was given. The new user will be created with this id.
- ```USER_GID```: optional. The group id of the newly created user. If not given, but ```USER_NAME``` is present, ```USER_UID``` will be used.

#### Commands
- ```start```: No-op
- ```shell <username=USER_NAME or root>```: Starts bash in the root directory in the name of ```username```.