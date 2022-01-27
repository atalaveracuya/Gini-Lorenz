

cap mkdir "$dataset"

if 1==1{
	mat MENAHO=J($periodo,31,0)
	forvalues i=1/$periodo {
	mat MENAHO[`i',1]=(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,22,23,24,25,26,27,28,34,37,77,78,84,85)
	}

}
mat list ENAHO
mat list MENAHO