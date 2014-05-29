all: litreview

litreview: litreview.tex litreview.bib
	pdflatex litreview
	bibtex litreview
	pdflatex litreview
	pdflatex litreview
	evince litreview.pdf

clean:
	rm -f litreview.aux litreview.bbl litreview.blg litreview.dvi litreview.out litreview.log *~* \#*
