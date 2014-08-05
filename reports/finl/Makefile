Ball: litreview

litreview: report.tex report.bib
	make clean
	pdflatex report 
	bibtex report 
	pdflatex report
	bibtex report
	pdflatex report
	pdflatex report
	make clean
	echo "hey" | mutt wmarsey@gmail.com -s "litreview" -a report.pdf

clean:
	rm -f *.aux *.bbl *.log *.xml *.toc *.blg *.dvi *.out *~* \#*
