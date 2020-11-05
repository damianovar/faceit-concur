PYTHON = python3
current_dir = $(notdir $(shell pwd))

PHONY : requirements
	- pip install -r requirements.txt

PHONY : pip 
	- python -m pip install --upgrade pip

PHONY : run 
	- make pip 
	- make requirements
	${PYTHON} -m ${current_dir}/script.py