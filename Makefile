#Target: setup
#Install all dependencies
setup:
	pip install -r requirements.txt

#Target: pipeline
#Executes the full analysis workflow: 

pipeline:
	python load_data.py
	python analysis.py

#Target: dashboard
#Launch the interactive dashboard
dashboard:
	python dashboard.py