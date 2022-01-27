replace estrato = 1 if dominio ==8 
gen area = estrato <6
replace area=2 if area==0
label define area 2 "Rural" 1 "Urbana"
label val area area