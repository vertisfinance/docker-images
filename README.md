# docker-images
Some useful Docker images used by Vertis.

## Concepts
All images are created from the ```vertisfinance/base``` base image. See details below.

### Minimal Image Size
This is a common goal image developers should take care of. There are some standard techniques and best practices to follow. Note that we do not go to extremes here: starting from a ```debian``` is OK for us.

### Configuration
Configuring a container based on an image should be easy and straightforward.
This is not easy to do right: There are too many places where one can put the same config value; sometimes you need to put the same value in multiple places.
In our setup, configuration can go to:
- the ```Dockerfile```


Main design goals are:
- Small image size.
- Maximum flexibility, easy configuration.
- The primary place of configuration is in environment variables, usage is documented in the provided compose files.
- User and group ids are configurable.
- Where services are normally configured by config files (postgres, nginx, etc.), there should be general ways to put these files inside containers. (See below.)
- Consistency checking at startup.
- Semafors to provide signal for dependent services.
- run.py as a startup mechanism.

### The Config Problem
Configuration can be hard to do in a non-redundant way. By redundancy I mean situations where you need to provide a value in environment variable, in a config file and maybe in ```run.py```. It can be hard to find a bug caused by only updating log file path in docker-compose.yml, but not in nginx.conf. 

While there are many possible solutions to this problem, most off them would restrict flexibility in an undesirable way. The best we can do is
- try to push config into environment variables and reuse them in config files.
- Supported variables should be well documented
- Provide as many startup check as possible

## Base

