install:
	mkdir -p video
	mkdir -p model
	conda env create --name VehicleDetection --file=environment.yml
	${CONDA_PREFIX}/envs/VehicleDetection/bin/pip install opencv-python
run:
	python main.py