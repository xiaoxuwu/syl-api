# syl-api

This repo is part of https://github.com/xiaoxuwu/ShopYourLinks. See the frontend source code here: https://github.com/xiaoxuwu/syl-frontend.git.

## 1 Introduction

This project contains the backend source code for ShopYourLinks, a [Shop Your Likes](https://shopyourlikes.com/) competitor to [Linktree](https://linktr.ee/). This document contains high-level information about this repository as well as set-up and run instructions for the backend microservice.

### 1.2 Maintainers

- Katie Luangkote
- Katrina Wijaya
- Xiaoxu (Carter) Wu
- Jennifer Xu
- Yun Xu

## 2 Set Up

1. Clone this repository: https://github.com/xiaoxuwu/syl-api.git

2. Set up Docker

    - Mac: https://docs.docker.com/docker-for-mac/install/

    - PC: https://docs.docker.com/toolbox/toolbox_install_windows/

3. Build container

    - Startup a terminal (Mac) or the docker-toolbox shell (PC), and type in the following commands:

    ```bash
    $ make build
    ```
    
4. Run first migration and create admin account for Django Admin (In another terminal (Mac) or the docker-toolbox shell (PC) window). You can use this to log in as a normal user. Note first line is run in shell (hence '$'), while second two lines are run in the docker container's shell (hence '#'). DO NOT include '$' or '#' in commands.

    ```
    $ make run-sh
    # python manage.py migrate
    # python manage.py createsuperuser
    
    ... follow prompts to create super user ...
    
    # exit
    ```


## 3 Run

Build container if necessary (when Carter says to)

```bash
$ make build
```

1. Once the container is built, you may run with the following methods:

    - For production and full integration testing:

     ```bash
     $ make run-prd
     ```

    - For development and simulating production deployment:

     ```bash
     $ make run-dev
     ```

    - For development and debugging (with pdb and full-debugger):

     ```bash
     $ make run-debug
     ```

2. Navigate to http://localhost:8000 at allowed routes with your browser to see the site.
    - Go to `/api` for API specifications

    - Go to `/admin` for the admin panel, and login with credentials from **2.4**

3. Use `CTRL+C` to quit the running server. To stop all containers, run:

     ```bash
     $ make exit
     ```
     
    - This command is automatically run before all Makefile run commands, so you do not need to do it unless you are using docker-compose manually.

  

## 4 Annotated Layout
```
.
├── Dockerfile <- setup file used during Docker image initialization
├── README.md <- this file
├── Makefile
├── docker-compose.yml <- setup file used during Docker image initialization
├── docker-entrypoint.sh <- file run to start the server
├── internal <- internal source folder containing most of the logic
│   ├── admin.py <- code to register models in admin panel
│   ├── apps.py
│   ├── migrations <- folder containing database migration files
│   │   ├── ...
│   ├── models.py <- Classes specifying the data model
│   │   ├── ...
│   ├── tests.py
│   ├── urls.py <- file specifying endpoint URLs and associated views
│   └── views.py <- functions that define the main server logic
├── manage.py <- main entry point for django server
├── shop_your_links <- folder containing media files and configurations
│   ├── media <- media files (images etc.)
│   │   ...
│   ├── settings.py <- site-wide configuration values
│   ├── urls.py <- top level endpoint specification
│   └── wsgi.py <- wsgi server configuration
├── requirements.txt <- requirements file specifying all python dependencies
└── static <- static css files
    └── css 
        └── style.css
```

## 5 Makefile Commands


`make init` configure system (run once)

`make build` build containers (ask Carter)

`run-dev` start containers with dev settings

`make run-prd` start containers with production settings

`make run-debug` start containers with pdb ability

`make run-sh` start sh in docker container

`make exit` shut down all containers
