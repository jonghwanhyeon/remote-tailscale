# remote-tailscale
## Usage
### Running a new container
Run the following commands to generate `docker-compose.yaml`.
```bash
$ git clone https://github.com/jonghwanhyeon/remote-tailscale {your-project-name}
$ cd {your-project-name} && python generate.py
```

Run the container as follows:
```
$ docker compose up --detach
```

Authenticate the machine by checking logs:
```
$ docker compose logs
```