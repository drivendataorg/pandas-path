reqs:
	pip install -r requirements-dev.txt

test: lint
	py.test -vv pandas_path/tests.py

lint:
	black .
	flake8 .

clean_pycache:
	find . -name *.pyc -delete && find . -name __pycache__ -delete

clean: clean_pycache
	rm -rf dist
	rm -rf pandas_path.egg-info

package: clean
	python setup.py sdist

distribute_pypitest: package
	twine upload --repository pypitest dist/*.tar.gz

distribute_pypi: package
	twine upload --repository pypi dist/*.tar.gz