# Savu API

A simple RESTful API on top of Savu that provides the core functionality of
`savu-config` and an abstract job queue interface.

This is deployed via a Docker image that extends an existing [Savu
image](https://github.com/DanNixon/dockerfiles/tree/master/savu). The base Savu
image defines what version of Savu the webapp will "appear as" (i.e. what
plugins are available, etc.).

If versioning is impelmented it is bets to do so via multiple API images created
from each version of the Savu image that is desired.

## API reference

### Plugin

- List all plugins  
  `GET /api/plugins`

- Search plugins by name  
  `GET /api/plugins?q=tomo`

- List plugin details  
  `GET /api/plugins/TomopyRecon`

### Process list

- List process lists in directory  
  `GET /api/process_list?path=/some/path`

- Show process list details  
  `GET /api/process_list?filename=/process_list.nxs`

- Upload a new process list  
  `POST /api/process_list?filename=/process_list.nxs`

- Overwrite/update an existing process list  
  `PUT /api/process_list?filename=/process_list.nxs`

- Delete a process list  
  `DELETE /api/process_list?filename=/process_list.nxs`

- Download a process list as a NeXus file  
  `GET /api/process_list/download?filename=/process_list.nxs`

### Data search

- Find data files in a given path  
  `GET /api/data/find?path=/some/path`

### Job queue

- Run a process list  
  `GET /api/jobs/[queue]/submit?process_list=/process_list.nxs&dataset=/data.nxs&output=/some/path`

- Query the status of a job  
  `GET /api/jobs/[queue]/[id]`

### Defaults

- Gets a list of default paths for things (data, process lists and output)  
  `GET /api/default_paths`

### DAWN data server

- Get dataset information (used to get data extents)  
  `GET /data/info`

- Get HDF5 tree structure (currently not used as it's returned in an unhelpful
  structure)  
  `GET /data/tree`

- Gets a slice of a file in a given format (used to generate dataset previews)  
  `GET /data/slice`
