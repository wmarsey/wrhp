all: litreview

litreview: litreview.tex litreview.bib
	make clean
	pdflatex litreview 
	bibtex litreview 
	pdflatex litreview
	bibtex litreview
	pdflatex litreview
	pdflatex litreview
	make clean
	#evince litreview.pdf
	echo "hey" | mutt wmarsey@gmail.com -s "litreview" -a litreview.pdf

clean:
	rm -f litreview.aux litreview.bbl litreview.blg litreview.dvi litreview.out *~* \#*
