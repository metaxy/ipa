
all: doc

doc: api-doc.pdf

api-doc.pdf: api-doc.tex
	pdflatex api-doc.tex

api-doc.tex: api-doc.rst
	rst2latex api-doc.rst >api-doc.tex

api-doc.rst: server.py server_test.py
	python3 server_test.py --apidoc
