default: build

init:
	sudo chmod +x docker-entrypoint.sh
build: init
	docker-compose build
run-dev: build
	docker-compose up
	exit
run-prd: build
	docker-compose up -d
run-debug: build
	docker-compose run --service-ports web
	exit
run-sh: build
	docker-compose run web sh
	exit
exit:
	docker-compose down
