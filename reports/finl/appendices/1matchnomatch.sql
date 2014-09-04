wm613=> SELECT SUM(
	CASE WHEN 
       	@(@(w.maths + 
	    w.citations + 
    	    w.filesimages + 
	    w.links + 
	    w.structure + 
	    w.normal) 
       	- @(t1.distance-
	    t2.distance)) = 0
       	THEN 1 
	ELSE 0 
	END) AS match,
       SUM(
       	CASE WHEN 
	@(@(w.maths + 
	w.citations + 
	w.filesimages + 
	w.links +
       	w.structure + 
	w.normal) - 
	@(t1.distance- 
	t2.distance)) <> 0 
	THEN 1 
	ELSE 0 
	END) AS non_match
       
       FROM wikitrajectory AS t1 
       JOIN wikiweights AS w 
       ON t1.revid2 = w.revid 
       AND t1.domain = w.domain 

       JOIN wikirevisions AS r 
       ON r.revid = w.revid 
       AND r.domain=w.domain 
       
       JOIN wikitrajectory AS t2 
       ON r.parentid = t2.revid2 
       AND r.domain = t2.domain;

 match | non_match 
-------+-----------
 30836 |     72250
(1 row)

(END)
