.PHONY: install run test demo docker

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -q

demo:
	python -m app.services.pipeline_demo

docker:
	docker compose up --build
