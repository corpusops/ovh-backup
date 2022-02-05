# Backup your OVH tied account infra back to YAML files

## Setup

- [Make your OVH Api token](https://api.ovh.com/createToken/?GET=/*&applicationName=corpusopsovhbackup&applicationDescription=corpusopsovhbackup&duration=Unlimited)
- Export envs vars needed to access to your token and backup needs

    ```sh
    cp .env.dist .env && $EDITOR .env
    ```

## What is exportable
- dns: export all dns zones (BIND format)

## Run
```sh
docker-compose run -v ./backup:/app/backup --rm backup
```

## install systemd wide and start at boot
```sh
./install.sh
```

## Exemples .env

- See [./.env.dist](./.env.dist)

