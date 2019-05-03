# Shop-Your-Links

## 1 Introduction

This project contains source code for ShopYourLinks, a [Shop Your Likes](https://shopyourlikes.com/) competitor to [Linktree](https://linktr.ee/). This document contains high-level information about this repository as well as set-up and run instructions.

### 1.1 Tech Stack

#### Core

- **Python 3**
- **Docker/Docker-Compose**: infrastructure and containerization
- **Django + DRF**: web framework
- **PostgreSQL**: database
- **Node.js + React**: front-end

#### Secondary

- Plotting library TBD  (plotting)

### 1.2 Team

- Katie Luangkote
- Katrina Wijaya
- Xiaoxu (Carter) Wu
- Jennifer Xu
- Yun Xu



## 2 Set Up

1. Clone this repository: https://github.com/xiaoxuwu/Shop-Your-Links.git

2. Set up Docker

    - Mac: https://docs.docker.com/docker-for-mac/install/

    - PC: https://docs.docker.com/toolbox/toolbox_install_windows/

3. Build container

    - Startup a terminal (Mac) or the docker-toolbox shell (PC), and type in the following commands:

    ```bash
    $ make build
    ```
    
4. First Migration and create Admin account for Django Admin (In another terminal (Mac) or the docker-toolbox shell (PC) window). You can use this to log in as a normal user.

    ```
    $ docker-compose run web sh
    # python manage.py migrate
    # python manage.py createsuperuser
    
    ... follow prompts to create super user ...
    
    # exit
    ```



## 3 Run

- Build container if necessary (when Carter says to)

  ```bash
  $ make build
  ```

- Once the container is built, you may run with the following methods:

  1. For production and full integration testing:

     ```bash
     $ make run-prd
     ```

  2. For development and simulating production deployment:

     ```bash
     $ make run-dev
     ```

  3. For development and debugging (with pdb and full-debugger):

     ```bash
     $ make run-debug
     ```

- Navigate to http://localhost:8000 with your browser to see the site.

  - Go to `/admin` for the admin panel, and login with credentials from **2.4**

- Use `CTRL+C` to quit the running server.

- To stop all containers, run:

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
│   ├── templates <- folder containing html files
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
├── start_dev_docker <- script to start terminal pointed at backend, not master
└── static <- static css files
    └── css 
        └── style.css
```
