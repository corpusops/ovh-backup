# Backup your OVH tied account infra back to YAML files

DISCLAIMER
============

**UNMAINTAINED/ABANDONED CODE / DO NOT USE**

Due to the new EU Cyber Resilience Act (as European Union), even if it was implied because there was no more activity, this repository is now explicitly declared unmaintained.

The content does not meet the new regulatory requirements and therefore cannot be deployed or distributed, especially in a European context.

This repository now remains online ONLY for public archiving, documentation and education purposes and we ask everyone to respect this.

As stated, the maintainers stopped development and therefore all support some time ago, and make this declaration on December 15, 2024.

We may also unpublish soon (as in the following monthes) any published ressources tied to the corpusops project (pypi, dockerhub, ansible-galaxy, the repositories).
So, please don't rely on it after March 15, 2025 and adapt whatever project which used this code.



## Setup

- [Make your OVH Api token](https://api.ovh.com/createToken/?GET=/*&applicationName=corpusopsovhbackup&applicationDescription=corpusopsovhbackup&duration=Unlimited)
- Export envs vars needed to access to your token and backup needs

    ```sh
    cp .env.dist .env && $EDITOR .env
    ```

## What is exportable
- dns: export all dns zones (BIND format)
- ipfo: export all IPFO infos

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

