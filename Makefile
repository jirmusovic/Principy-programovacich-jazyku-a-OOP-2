PY = python3.10
SCRIPT = interpret.py

run:
	$(PY) $(SCRIPT) --source=tests/xml.xml --input=input

test:
	rm -f out.html
	php test.php --directory=ipp-2023-tests/both/ --parse-script=parse.php --recursive > out.html

test_int:
	rm -f out1.html
	php test.php --int-only --recursive --directory=ipp-2023-tests/interpret-only/ > out1.html

extended:
	rm -f out2.html
	php test.php --int-only --recursive --directory=ipp-2023-tests/extended/ > out2.html
