# Shop-Your-Links

## 1 Introduction
This project contains source code for a ShopYourLinks, a ShopYourLikes competitor to LinkTree. This document contains high-level information about this repository as well as set-up and run instructions.

### 1.1 Tech Stack

#### Core

- Python
- Docker (infrastructure and containerization)
- Django + DRF (web framework)
- Postgresql (database)  
- Node.js + React (front-end)

#### Secondary

- Plotting library TBD  (plotting)

## 2 Set Up

1. Clone this repository

2. Set up Docker

    Mac: https://docs.docker.com/docker-for-mac/install/

    PC: https://docs.docker.com/toolbox/toolbox_install_windows/

3. Build container

    Startup a terminal (Mac) or the docker-toolbox shell (PC), and type in the following commands:

    ```
    make build
    ```
    
4. First Migration and create Admin account for Django Admin (In another terminal (Mac) or the docker-toolbox shell (PC) window). You can use this to log in as a normal user.

    ```
    docker-compose run web sh
    python manage.py migrate
    python manage.py createsuperuser
    
    ... follow prompts to create super user ...
    
    exit
    ```

## 3 Run

Once the container is built, you may run with two methods:

For production and full integration testing:

```
make run-prd
```

For development and simulating production deployment:

```
make run-dev
```

For development and debugging (with pdb and full-debugger):

```
make run-debug
```

You may now go to http://localhost:8000 with your browser to see the site. Go to /admin for admin panel, and
log in with credentials from 2.5

## 3.1 Quitting

Use Ctrl+C to quit the running server. To stop all containers, run:

```
make exit
```

This command is automatically run before all makefile run commands, so you do not need to do it unless you are using docker-compose manually.

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
