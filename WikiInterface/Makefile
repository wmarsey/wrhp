all:
	wget https://gitlab.doc.ic.ac.uk/wm613/inidividual-project/repository/archive.tar
	tar -xvf archive.tar
	rm -f archive.tar
	cd inidividual-project.git; mv WikiInterface/ ..
	rm -rf inidividual-project.git
	#psql WikiInterface/schema.sql
	python WikiInterface/automaton.py
