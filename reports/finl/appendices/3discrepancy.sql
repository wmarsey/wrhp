      SELECT AVG( 
        @(@(w.maths + 
	 w.citations + 
	 w.filesimages + 
	 w.links +
	 w.structure + 
	 w.normal) 
	 - @(t1.distance 
	   - t2.distance)) /
	 CASE WHEN 
	 r.size = 0 
	 THEN 
	 1 
	 ELSE 
	 r.size::float) AS average_discrepency 

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

 average_discrepency 
---------------------
    22180.7321410815
(1 row)

(END)
