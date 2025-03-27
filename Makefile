install-backend:
	chmod +x backend/install.sh
	chmod +x backend/run.sh
	cd backend && ./install.sh

install-frontend:
	chmod +x frontend/install.sh
	chmod +x frontend/run.sh
	cd frontend && ./install.sh

install: install-backend install-frontend
	@echo "Tempo Task has been successfully installed!"

run-backend:
	cd backend && ./run.sh

run-frontend:
	cd frontend && ./run.sh

start: run-backend run-frontend
	@echo "Tempo Task is now running!"

.DEFAULT_GOAL := install
