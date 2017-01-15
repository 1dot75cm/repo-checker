
all: gettext build

test:
	pip install -r requirements-test.txt
	tox

gettext:
	@echo "Generate qm file..."
	@for i in zh_CN zh_TW; do \
	    pylupdate5 -noobsolete checker/frontends/*.py -ts locale/$$i.ts; \
	    lrelease-qt5 locale/$$i.ts -qm checker/locale/$$i.qm; \
	done

build:
	@echo "Build source and binary package..."
	@python setup.py sdist bdist_wheel

upload: build
	@echo "Upload package to PyPI..."
	@python setup.py upload
