init:
	sudo chmod +x docker-entrypoint.sh
build: init
	docker-compose build
run-dev: exit
	docker-compose up
run-prd: exit
	docker-compose up -d
run-debug: exit
	docker-compose run --service-ports web
run-sh: exit
	docker-compose run web sh
exit:
	docker-compose down