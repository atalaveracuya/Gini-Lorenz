***********************************
global periodo=$final - $inicio + 1
global ini=$inicio-2000 
global fin=$final-2000  

display "$periodo"
display "$ini"
display "$fin"

*codigo de encuestas 
clear 
input int codenc int anio
280 2004
281	2005
282	2006
283	2007
284	2008
285	2009
279	2010
291	2011
324	2012
404	2013
440	2014
498	2015
546	2016
603	2017
634	2018
687	2019
737	2020
end

keep if anio>=$inicio & anio<=$final  


**matrix codigo de encuesta - ENAHO 
mkmat codenc, mat(ENAHO)
mat list ENAHO



