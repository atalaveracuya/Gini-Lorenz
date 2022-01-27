*gasto nominal per capita 
gen gnpcm=(gashog2d/(12*mieperho))
*gasto real per capita 
gen gpcm=(gashog2d/(12*mieperho))/ld
*ingreso real per capita 
gen ipcm=(inghog1d/(12*mieperho))/ld