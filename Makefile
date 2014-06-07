.PHONY: doc dist

all: generate run

generate:
		make -C resources generate

run:
		cd src; python afefuc.py

clean:
		rm -rf dist
		for file in `find src -iname *.pyc`; do rm $$file; done

doc:
		make -C doc html

dist: clean generate doc
		mkdir -p dist/app
		cp -r src/* dist/app
		rm -rf dist/private
		rm dist/app/*.auc
		cp -r doc/_build/html dist
		mv dist/html dist/doc
		cp resources/call/afefuc.sh dist
		cp resources/call/afefuc.bat dist
		-cp private/rpo.auc dist/
		-rm dist.zip
		zip dist.zip -r dist/*
