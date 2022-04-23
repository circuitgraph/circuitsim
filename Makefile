
doc : docs/index.html

docs/index.html : circuitsim/* docs/templates/*
	pdoc --html circuitsim --force --template-dir docs/templates
	cp -r html/circuitsim/* docs

test :
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	python3 -m unittest
	python3 -m doctest circuitsim/*.py

test_% :
	python3 -m unittest tests/test_$*.py

dist : setup.py
	rm -rf dist/* build/* circuitsim.egg-info
	python3 setup.py sdist bdist_wheel

test_upload: dist
	python3 -m twine upload --repository testpypi dist/*

upload : dist
	python3 -m twine upload dist/*

install:
	pip3 install .

install_editable :
	pip3 install -e .
