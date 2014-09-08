      SELECT AVG(
	@(@(w.maths + 
	w.citations + 
	w.filesimages + 
	w.links +
	w.structure + 
	w.normal) 
	- @(t1.distance - 
	t2.distance))
	/ CASE WHEN 
	CASE WHEN 
	@(w.maths + 
	w.citations + 
	w.filesimages + 
	w.links +
	w.structure + 
	w.normal) > @(t1.distance - 
	t2.distance)
	THEN
	@(w.maths + 
	w.citations + 
	w.filesimages + 
	w.links +
	w.structure + 
	w.normal)::float
	ELSE
	@(t1.distance - 
	t2.distance)::float
	END
	= 0 
	THEN 1
	ELSE
	CASE WHEN 
	@(w.maths + 
	w.citations + 
	w.filesimages + 
	w.links +
	w.structure + 
	w.normal) > @(t1.distance - 
	t2.distance)
	THEN
	@(w.maths + 
	w.citations + 
	w.filesimages + 
	w.links +
	w.structure + 
	w.normal)::float
	ELSE
	@(t1.distance - 
	t2.distance)::float
	END
	END) AS average_discrepancy   
       
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

 average_discrepancy_percent 
-----------------------------
      0.386195332179081
(1 row)

(END)
