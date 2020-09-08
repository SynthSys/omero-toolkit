# OMERO CLI Batch

This Python script uploads data to an OMERO server in batches


# Description

The 'tag manager' command line tool can be used for automatically cleaning and rationalising tag 
annotations on a target remote OMERO server instance.

## Tag Manager

The tag manager - `src/tag_manager/tag_manager.py` offers two main features:

1. An automated cleaning function which will query the specified OMERO server 
database and find any tag annotations that share identical label text values 
and descriptions. Any tags like this are merged into one tag, all objects linked
to duplicate tags are re-linked to the target tag and the duplicate tags are 
then deleted.
2. A tag curation feature that allows the user to specify a target tag ID or 
label text value along with a list of tag IDs/labels which are to be merged into 
the target tag and then deleted. As with (1), all objects linked with tags to be 
merged are re-linked with the target tag. 

# Requirements and running

You must have an OMERO Python virtual environment and the OMERO CLI tools
present in the file system. The best way to achieve this is by deploying
the OMERO server Docker images (https://hub.docker.com/r/openmicroscopy/omero-server)
and running them with the data directory mounted to the container.

You can use the included requirements files to create the required Python/Conda
virtual environments as follows:

```shell script
# Conda
$ conda create --name omero_cli_batch --file requirements_conda.txt

# Pip
$ python -m venv /path/to/omero_cli_batch
$ source /path/to/omero_cli_batch/bin/activate
$ pip install -r requirements.txt
```

If you are using the Docker methods below, you can use the requirements files to install
the dependencies into the existing Conda or Python virtual environment as follows:

```shell script
# Conda (Python 2, python-omero 5.4.10)
$ conda install --file requirements_conda.txt

# Pip (Python 3, omero-py 5.6.1)
$ pip install -r requirements.txt
``` 

## Tag Manager

The easiest way to run the tag manager is using the CLI in 
`src/omero_cli_batch/tag_manager_cli.py`. Available options are:

```shell script
optional arguments:
  -h, --help            show help message and exit

  # Connection parameters
  -u username, --username username
                        specifies the username for connection to the remote
                        OMERO server
  -s server, --server server
                        specifies the server name of the remote OMERO server
                        to connect
  -o [port], --port [port]
                        specifies the port on the remote OMERO server to
                        connect (default is 4064)
  -a, --password        hidden password prompt for connection to the remote
                        OMERO server

  # Tag management parameters
  -i, --target-tag-id
                        Omero ID of the destination tag for merging and
                        linking objects to
  -l, --target-tag-label
                        Label of the destination tag for merging and linking
                        objects to
  -e, --tag-labels-to-remove
                        List of regex strings for tag labels which are to be
                        merged and removed on the Omero server
  -r, --tags-to-remove
                        List of tag labels which are to be merged and removed
                        on the Omero server
  -d, --dry-run         Instructs the tag manager to report intended changes
                        rather than actually perform the merge and tag
                        deletion process. Non-destructive and allows you to 
                        see what will be changed without actually doing so.
```

Example commands for running the tag manager CLI:

```shell script
$ cd src

# automatically remove all identical duplicate tags and merge all 
# associated datasets/images into the first 'original' tag; no 
# extra parameters required beyond username and server
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3

# merge all datasets/images associated with tags withs labels 'arch%' and 
# 'amoeb%' into one existing tag labelled 'amoebozoa'
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3 -l amoebozoa \
  -e arch% amoeb%

# merge all datasets/images associated with tags withs labels 'arch%' and 
# 'amoeb%' and tags with IDs 245 and 253 into one existing tag labelled 
# 'amoebozoa'
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3 -l amoebozoa \
  -e arch% amoeb% -r 245 253

# merge all datasets/images associated with tags with labels 'cell wall' 
# into one existing tag with label 'cell'
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3 -l cell \
  -e "cell wall"

# Dry Run: merge all datasets/images associated with tags with labels 
# 'cell wall' into one existing tag with label 'cell'
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3 -l cell \
  -e "cell wall" -d

# error: Cannot specify both target tag ID and target tag label; use 
# one or the other
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3 -i 233 \
  -l amoebozoa -e arch% amoeb%

# merge all datasets/images associated with tags with labels 'arch%' 
# and 'amoeb%' into one existing tag with ID 233
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3 -i 233 \
  -e arch% amoeb%

# merge all datasets/images associated with tags with labels 'arch%' 
# and 'amoeb%' and tags with IDs 245 and 253 into one existing tag with ID 233
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3 -i 233 \
  -e arch% amoeb% -r 245 253

# Dry Run: merge all datasets/images associated with tags with labels 'arch%' 
# and 'amoeb%' and tags with IDs 245 and 253 into one existing tag with ID 233
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3 -i 233 \
  -e arch% amoeb% -r 245 253 -d

# merge all datasets/images associated with tags with label 
# '"Screaming" Hairy l'éléphan%' into one existing tag with ID 233
$ python -m tag_manager.tag_manager_cli -u root -s 172.17.0.3 -i 233 \ 
    -e "\"Screaming\" Hairy l'éléphan%"
```

An alternative CLI tool for the tag manager is in 
`src/omero_cli_batch/tag_manager_prompt_cli.py`. Rather than providing all
of the arguments in one CLI execution line, the user simply provides their
username, host and port (if non-default) in the initial line and then the
program prompts the user for further input. For example:

```shell script
$ cd src
$ python -m tag_manager.tag_manager_prompt_cli -u root -s 172.17.0.3
target_tag_id: Omero ID of the destination tag for merging and linking objects to
> 233
target_tag_label: Label of the destination tag for merging and linking objects to
>
tag_labels_to_remove: List of regex strings for tag labels which are to be merged and removed on the Omero server
> arch% amoeb%
tags_to_remove: List of tag IDs which are to be merged and removed on the Omero server
> 245 253
dry_run: Instructs the tag manager to report intended changes rather than actually perform the merge and tag deletion process. Non-destructive and allows you to see what will be changed without actually doing so.
>
Password:
``` 

# Note

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
