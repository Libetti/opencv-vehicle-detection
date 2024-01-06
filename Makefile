install:
	mkdir -p video
	mkdir -p model
	conda env create --name VehicleDetection --file=environment.yml
	conda activate VehicleDetection

run:
	python main.py