MM2XML=../../src/utils/mm2xml.py
OUTPUT=../../src/generated/testcases

generate:
		for input in *.mm; do\
			filename=`basename $$input .mm`;\
			$(MM2XML) $$input $(OUTPUT)/$$filename.xml;\
		done;
