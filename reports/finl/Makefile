all: litreview

litreview: thesis.tex thesis.bib
	make clean
	pdflatex thesis 
	bibtex thesis
	pdflatex thesis
	bibtex thesis
	pdflatex thesis
	pdflatex thesis
	make clean
	echo "hey" | mutt wmarsey@gmail.com -s "finalreport" -a thesis.pdf
	evince thesis.pdf

clean:
	rm -f *.aux *.bbl *.log *.xml *.toc *.blg *.dvi *.out *~* \#*
