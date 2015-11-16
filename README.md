# docker-images
Some useful Docker images used by Vertis.

## Concepts
All images are created from the ```vertisfinance/base``` base image.
Main design goals are:
- Reduce image size
- Maximum flexibility threw easy configuration
- The primary place of configuration is in environment variables, usage is documented in the provided compose files.
- Some (most of the) services use their own config file (postgresql, nginx, uwsgi, etc.). Providing these config options in environment variables would lead to unnecessary complexity and steeper learning curve, which is generally bad. We do not want to restrict how users want to handle config files (compile them into the image or provide a volume on the host with these files), the location of the config files should be provided in environment variables.

## Base

