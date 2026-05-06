import pandas as pd



def calcular\_mensualidad(precio, enganche\_pct, tasa\_anual, meses\_credito):

&#x20;   """

&#x20;   Calcula el pago mensual del crédito automotriz y el monto de enganche.

&#x20;   """

&#x20;   enganche = precio \* (enganche\_pct / 100)

&#x20;   monto\_credito = precio - enganche

&#x20;   

&#x20;   if tasa\_anual == 0 or meses\_credito == 0:

&#x20;       return (monto\_credito / meses\_credito) if meses\_credito > 0 else 0, enganche

&#x20;       

&#x20;   tasa\_mensual = (tasa\_anual / 100) / 12

&#x20;   mensualidad = (monto\_credito \* tasa\_mensual) / (1 - (1 + tasa\_mensual) \*\* -meses\_credito)

&#x20;   

&#x20;   return mensualidad, enganche



def calcular\_costos\_operativos(tipo\_auto, precio\_auto, km\_anuales, rendimiento\_gas, rendimiento\_elec,

&#x20;                              precio\_gas, precio\_elec, costo\_mant\_base\_anual, pct\_uso\_elec=0):

&#x20;   """

&#x20;   Calcula los gastos operativos mensuales (Energía, Mantenimiento, Tenencia).

&#x20;   Factores de mantenimiento: Gasolina 100%, HEV 74%, PHEV 54%, BEV 31%.

&#x20;   """

&#x20;   # 1. GASTO DE MANTENIMIENTO

&#x20;   factores\_mant = {

&#x20;       'Gasolina': 1.0,

&#x20;       'HEV': 0.74,

&#x20;       'PHEV': 0.54,

&#x20;       'BEV': 0.31

&#x20;   }

&#x20;   factor = factores\_mant.get(tipo\_auto, 1.0)

&#x20;   mantenimiento\_mensual = (costo\_mant\_base\_anual \* factor) / 12



&#x20;   # 2. GASTO DE ENERGÍA / COMBUSTIBLE

&#x20;   km\_mensuales = km\_anuales / 12

&#x20;   costo\_energia\_mensual = 0

&#x20;   

&#x20;   if tipo\_auto in \['Gasolina', 'HEV']:

&#x20;       costo\_energia\_mensual = (km\_mensuales / rendimiento\_gas) \* precio\_gas

&#x20;   elif tipo\_auto == 'BEV':

&#x20;       costo\_energia\_mensual = (km\_mensuales / rendimiento\_elec) \* precio\_elec

&#x20;   elif tipo\_auto == 'PHEV':

&#x20;       km\_elec = km\_mensuales \* (pct\_uso\_elec / 100)

&#x20;       km\_gas = km\_mensuales - km\_elec

&#x20;       costo\_energia\_mensual = ((km\_elec / rendimiento\_elec) \* precio\_elec) + ((km\_gas / rendimiento\_gas) \* precio\_gas)



&#x20;   # 3. TENENCIA (Promedio 3% anual para combustión. Exento para HEV/PHEV/BEV en centro de México)

&#x20;   tenencia\_mensual = (precio\_auto \* 0.03) / 12 if tipo\_auto == 'Gasolina' else 0



&#x20;   return costo\_energia\_mensual, mantenimiento\_mensual, tenencia\_mensual



def proyectar\_costos\_acumulados(meses\_proyeccion, enganche, mensualidad, costo\_energia, 

&#x20;                               costo\_mant, costo\_tenencia, meses\_credito):

&#x20;   """

&#x20;   Genera una lista con el costo total acumulado mes a mes para encontrar el Break-Even.

&#x20;   """

&#x20;   acumulado = enganche

&#x20;   costos\_por\_mes = \[]

&#x20;   

&#x20;   for mes in range(1, meses\_proyeccion + 1):

&#x20;       pago\_auto = mensualidad if mes <= meses\_credito else 0

&#x20;       gasto\_total\_mes = pago\_auto + costo\_energia + costo\_mant + costo\_tenencia

&#x20;       acumulado += gasto\_total\_mes

&#x20;       costos\_por\_mes.append(acumulado)

&#x20;       

&#x20;   return costos\_por\_mes

