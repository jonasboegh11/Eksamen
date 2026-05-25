up:
	cd voltedge/charging-session-service && docker-compose up --build -d

down:
	cd voltedge/charging-session-service && docker-compose down

logs:
	cd voltedge/charging-session-service && docker-compose logs -f

restart:
	cd voltedge/charging-session-service && docker-compose down && docker-compose up --build -d

clean:
	cd voltedge/charging-session-service && docker-compose down -v