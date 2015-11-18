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
- Service config files should be placed to ```/opt/config``` and copied to an other location during startup. When a config value is given in an environment variable and need to be referenced in a ```.conf``` file, use variable substitution / templating.
- Do reasonable checking at startup time.

### Templating
Example syntax (in ```whatever.conf```):
```
logging: file
log_path: {{LOG_PATH}}
```
In the above case ```LOG_PATH``` must be given as an environment variable. During container startup this will be substituted and the file will be copied to an other location.

### ```run.py```

### User, group IDs

### Semafors

## Images

### ```vertisfinance/base```


