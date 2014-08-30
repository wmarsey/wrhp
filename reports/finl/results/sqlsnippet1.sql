-- SELECT r.pageid			AS pageid,
--        t1.revid2		AS parentid, 
--        t2.revid2    		AS childid, 
--        (w.maths + 
--         w.citations +
-- 	w.filesimages +
-- 	w.links +
-- 	w.structure +
-- 	w.normal)		AS pairdist, 
--        @(t1.distance-
--          t2.distance)		AS trajdifference, 
--        @(@(w.maths + 
--            w.citations +
-- 	   w.filesimages +
-- 	   w.links +
-- 	   w.structure +
-- 	   w.normal) - 
--        	 @(t1.distance-
--    	   t2.distance))	AS difference,
-- 	  (@(@(w.maths + 
--            w.citations +
-- 	   w.filesimages +
-- 	   w.links +
-- 	   w.structure +
-- 	   w.normal) - 
--        	 @(t1.distance-
--    	   t2.distance))/
-- 	   r.size::float)	AS discrepency,
-- 	   r.size 		AS size
       
--        FROM wikitrajectory AS t1 
--        JOIN wikiweights AS w 
--        ON t1.revid2 = w.revid 
--        AND t1.domain = w.domain 

--        JOIN wikirevisions AS r 
--        ON r.revid = w.revid 
--        AND r.domain=w.domain 
       
--        JOIN wikitrajectory AS t2 
--        ON r.parentid = t2.revid2 
--        AND r.domain = t2.domain;

----------
-- Gives average discrepancy between edit differences, using the
-- difference between the two edit distances
---------- 
SELECT AVG(
	@(@(w.maths + 
	w.citations + 
	w.filesimages + 
	w.links +
	w.structure + 
	w.normal) 
	- @(t1.distance - 
	t2.distance))) AS average_difference
       
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

----------
-- Gives average discrepancy between edit differences, using the
-- percentage of the difference to the overall revision size
---------- 
SELECT AVG(
	@(@(w.maths + 
	w.citations + 
	w.filesimages + 
	w.links +
	w.structure + 
	w.normal) 
	- @(t1.distance - 
	t2.distance))
	/ r.size::float) AS average_discrepency   
       
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

----------
-- Gives average discrepancy between edit differences, using the
-- percentage of the difference to the overall revision size
---------- 
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
	END) AS average_discrepency   
       
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

----------
-- counts matches and mismatches
---------- 
SELECT SUM(
	CASE WHEN 
       	@(@(w.maths + w.citations + w.filesimages + w.links + w.structure + w.normal) 
       	- @(t1.distance-t2.distance)) = 0
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
