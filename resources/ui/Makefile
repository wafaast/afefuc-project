generate:
		for input in *.ui; do\
			filename=`basename $$input .ui`;\
			pyuic4 $$input > ../../src/generated/ui/$$filename.py;\
		done;
