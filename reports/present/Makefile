all:	
	pdflatex presentation
	bibtex presentation
	pdflatex presentation
	#adoberead presentation.pdf
	echo "hey" | mutt wmarsey@gmail.com -s "presentation" -a presentation.pdf
	evince presentation.pdf
