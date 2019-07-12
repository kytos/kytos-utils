prepare:
	pip3.7 install --upgrade pip setuptools wheel twine

clean:
	rm -rf build/ dist/ *.egg-info/

build: clean
	python3.7 setup.py sdist bdist_wheel

testupload: build
	twine upload -r pypitest dist/*

upload: build
	twine upload dist/*
