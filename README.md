# omero-toolkit

This toolkit includes Docker files and software utilities designed to assist researchers to deposit their microscopy data into an OMERO server.

## Docker Files (OMEROConnect)

The Docker files in the toolkit provide support for uploading to and 
querying OMERO servers, the Open Microscopy Environment image data 
repository platform. The Docker files are duplicated from the original
OMEROConnect repository.

## Software Utilities

Included with the toolkit are two main utilities for supporting (meta)data deposition and curation activities: the 'tag manager' and the 'batch upload' scripts.

## Toolkit Structure
The toolkit is intended to be deployed as Docker containers. There are three container images: `omero_base`, `omero_uploader` and `omero_jupyter`. The Jupyter Docker container image inherits from the uploader image which in turn inherits from the base image.

## Using the Toolkit

### Running the Pre-built Toolkit Docker Images

The easiest way to use the toolkit is simply to pull and run the pre-built 
Docker images that are provided by the OMEROConnect project. Pull the latest
images with the following command:

```
docker pull biordm/omero-connect:omero_uploader
docker pull biordm/omero-connect:omero_jupyter
```

Once the OMEROConnect images are downloaded to the local Docker image repository, they can be run with slight modifications to the commands given previously, for instance:
```
docker run -t -d --name omero-uploader -v /C/projects/Omero_data:/var/data/omero_data -v /<path>/<to>/<omero-toolkit>:/home/jovyan/omero-toolkit --entrypoint /bin/bash biordm/omero-connect:omero_uploader
```
```
docker run --name omero-jupyter -p 8888:8888 -v 'D:\projects\omero_connect_demo\notebooks:/home/jovyan/work/query_notebooks:rw' -v /<path>/<to>/<omero-toolkit>:/home/jovyan/omero-toolkit omero_jupyter
```
To access a `bash` terminal in the resulting Docker containers, run commands such as:
```
docker exec -it omero-uploader /bin/bash
```

### Building and Running the Toolkit Docker Images Manually
Please see the README.md in the `docker` directory for instructions on building
the Docker images yourself.