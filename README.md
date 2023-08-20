## Repository Structure

Since I can't create more repositories with the Uni github account, I use the mono-repo substructure. The project's task is divided into different microservices: 
- `server`: for setting up API server 
- `db`: for setting up database 

Other microservices that can be added (If time permits): 
- `login`: handles client login and grant permission based on privillege levels. 
- `analytics`: software analytic
- `routing`: more complex routing algorithms

The location of each microservice is under: 

- `src`: source code for the project 
  - `src/db`: database microservice. At the moment it does nothing yet. Might be a good place to store data dump for test cases.
  - `src/server`: uvicorn database API server. 
- `test`: test files. 
- `doc`: documentation 

Orchestration of the microservices is achieved through `compose.yaml`

## Installing dependencies 

 Since we are using `docker` for development and deployment, the only prerequisite is to have `docker` and `docker compose` installed. Refer to the following links for setup instructions: [Windows](https://docs.docker.com/desktop/windows/permission-requirements/), [Linux](https://docs.docker.com/desktop/install/linux-install/). 

## Running MySQL database container: 

Run 

```
docker compose up mysql
```

This will pull the image `mysql:8.0` from docker repository and create a container instance of it. At start up, it creates the database `SEP`, which is used by the API server. 

## Running `sep_server` service container:

Run

```
docker compose build 
```

This will build the `sep_server` image defined under `src/server/Dockerfile` and install the required Python dependencies. After this is finished, make sure that the database server is up and running (see previous post or run `docker ps` and confirm that mysql container is running). Once this is done, run:  

```
docker compose up sep_server
```

This also exposes port `8000:8000` to the docker host (your local environment). Now you should be able to query and update the database using the provided APIs.

## Examples:

### Adding devices
```
curl -X 'POST' \
  'http://127.0.0.1:8000/add/devices/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
{
  "name": "A"
},
{
  "name": "B"
},
{
  "name": "C"
},
{
  "name": "D"
}
]'
```

### Adding connections:

```
curl -X 'POST' \
  'http://127.0.0.1:8000/add/connections/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
{
  "src": "A",
  "dst": "B",
  "cost": 24
},
{
  "src": "A",
  "dst": "C",
  "cost": 3
},
{
  "src": "A",
  "dst": "D",
  "cost": 20
},
{
  "src": "C",
  "dst": "D",
  "cost": 12
}
]'
```

### See available devices: 

```
curl http://127.0.0.1:8000/devices
```

### See available connections:

```
curl http://127.0.0.1:8000/connections
```

### See best path from src:

```
curl http://127.0.0.1:8000/path?src=A
```

## Stopping the program:

```
docker compose down
```