# If needed, can reduce makefile as bash command
#!/bin/bash
SOURCES = Meadors-Cone-CrossCorr
CC = pdflatex
BIB = bibtex

all: compilePost compileBib compilePre

compilePre:
	$(CC) $(SOURCES)

compileBib: compilePre
	-$(BIB) $(SOURCES)

compilePost: compileBib compilePre
	$(CC) $(SOURCES)
	$(CC) $(SOURCES)
	$(CC) $(SOURCES)

