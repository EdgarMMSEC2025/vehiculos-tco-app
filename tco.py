import numpy as np
from typing import List, Dict, Union

def calcular_pago_mensual(monto_prestamo: float, plazo_meses: int, tasa_anual_pct: float) -> float:
    """
    Calcula el pago mensual de un préstamo usando el método de amortización francesa (cuotas fijas).
    """
    if monto_prestamo <= 0 or plazo_meses <= 0:
        return 0.0
    
    if tasa_anual_pct == 0.0:
        return monto_prestamo / plazo_meses
        
    tasa_mensual = (tasa_anual_pct / 100.0) / 12.0
    pago = monto_prestamo * (tasa_mensual * (1 + tasa_mensual)**plazo_meses) / ((1 + tasa_mensual)**plazo_meses - 1)
    return pago

def calcular_costo_energia_mensual(
    km_anual: float, 
    tipo: str,
    precio_gasolina: float, 
    precio_electricidad: float,
    consumo_l_100km: float = 0.0, 
    consumo_kwh_100km: float = 0.0,
    pct_km_ev_phev: float = 0.0
) -> float:
    """
    Calcula el costo de energía mensual promedio basado en los parámetros del vehículo.
    Tipos válidos: 'GAS', 'HEV', 'PHEV', 'BEV'
    """
    km_mensual = km_anual / 12.0
    
    if tipo in ['GAS', 'HEV']:
        litros_mensuales = (km_mensual / 100.0) * consumo_l_100km
        return litros_mensuales * precio_gasolina
        
    elif tipo == 'BEV':
        kwh_mensuales = (km_mensual / 100.0) * consumo_kwh_100km
        return kwh_mensuales * precio_electricidad
        
    elif tipo == 'PHEV':
        km_ev = km_mensual * (pct_km_ev_phev / 100.0)
        km_gas = km_mensual - km_ev
        
        costo_ev = (km_ev / 100.0) * consumo_kwh_100km * precio_electricidad
        costo_gas = (km_gas / 100.0) * consumo_l_100km * precio_gasolina
        return costo_ev + costo_gas
        
    return 0.0

def proyeccion_costo_acumulado(
    precio: float, 
    enganche: float, 
    plazo_meses: int, 
    tasa_anual: float, 
    comision_apertura_pct: float,
    costo_energia_mensual: float,
    meses_proyeccion: int = 120
) -> Dict[str, Union[float, List[float]]]:
    """
    Genera la serie de tiempo del costo acumulado mes a mes.
    Retorna un diccionario con los KPIs y la lista de costos acumulados.
    """
    monto_prestamo = max(0.0, precio - enganche)
    comision_apertura = monto_prestamo * (comision_apertura_pct / 100.0)
    
    pago_mensual = calcular_pago_mensual(monto_prestamo, plazo_meses, tasa_anual)
    
    # El mes 0 incluye el desembolso inicial: enganche + comisión
    costo_actual = enganche + comision_apertura
    serie_acumulada = [costo_actual]
    
    for mes in range(1, meses_proyeccion + 1):
        if mes <= plazo_meses:
            costo_actual += pago_mensual
        
        costo_actual += costo_energia_mensual
        serie_acumulada.append(costo_actual)
        
    total_pagado_auto = enganche + comision_apertura + (pago_mensual * plazo_meses)
        
    return {
        "pago_mensual": pago_mensual,
        "comision_apertura": comision_apertura,
        "total_pagado_auto": total_pagado_auto,
        "costo_energia_anual": costo_energia_mensual * 12,
        "serie_acumulada": serie_acumulada
    }

def encontrar_break_even(serie_base: List[float], serie_comparar: List[float]) -> int:
    """
    Encuentra el mes en el que la serie_comparar se vuelve más barata (estrictamente menor)
    que la serie_base. Si no sucede, retorna -1.
    """
    for mes, (costo_base, costo_comp) in enumerate(zip(serie_base, serie_comparar)):
        if costo_comp < costo_base:
            return mes
    return -1
