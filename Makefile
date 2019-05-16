default: build

init:
	sudo chmod +x docker-entrypoint.sh
build: init
	docker-compose build
run-dev:
	docker-compose up
	exit
run-prd: 
	docker-compose up -d
run-debug: 
	docker-compose run --service-ports web
	exit
run-sh: 
	docker-compose run web sh
	exit
exit:
	docker-compose down
