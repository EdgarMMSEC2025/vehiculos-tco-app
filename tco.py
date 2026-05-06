import pandas as pd

def calcular_mensualidad(precio, enganche_pct, tasa_anual, meses_credito):
    """
    Calcula el pago mensual del crédito automotriz y el monto de enganche.
    """
    enganche = precio * (enganche_pct / 100)
    monto_credito = precio - enganche
    
    if tasa_anual == 0 or meses_credito == 0:
        return (monto_credito / meses_credito) if meses_credito > 0 else 0, enganche
        
    tasa_mensual = (tasa_anual / 100) / 12
    mensualidad = (monto_credito * tasa_mensual) / (1 - (1 + tasa_mensual) ** -meses_credito)
    
    return mensualidad, enganche

def calcular_costos_operativos(tipo_auto, precio_auto, km_anuales, rendimiento_gas, rendimiento_elec,
                               precio_gas, precio_elec, costo_mant_base_anual, pct_uso_elec=0):
    """
    Calcula los gastos operativos mensuales (Energía, Mantenimiento, Tenencia).
    Factores de mantenimiento: Gasolina 100%, HEV 74%, PHEV 54%, BEV 31%.
    """
    # 1. GASTO DE MANTENIMIENTO
    factores_mant = {
        'Gasolina': 1.0,
        'HEV': 0.74,
        'PHEV': 0.54,
        'BEV': 0.31
    }
    factor = factores_mant.get(tipo_auto, 1.0)
    mantenimiento_mensual = (costo_mant_base_anual * factor) / 12

    # 2. GASTO DE ENERGÍA / COMBUSTIBLE
    km_mensuales = km_anuales / 12
    costo_energia_mensual = 0
    
    if tipo_auto in ['Gasolina', 'HEV']:
        costo_energia_mensual = (km_mensuales / rendimiento_gas) * precio_gas
    elif tipo_auto == 'BEV':
        costo_energia_mensual = (km_mensuales / rendimiento_elec) * precio_elec
    elif tipo_auto == 'PHEV':
        km_elec = km_mensuales * (pct_uso_elec / 100)
        km_gas = km_mensuales - km_elec
        costo_energia_mensual = ((km_elec / rendimiento_elec) * precio_elec) + ((km_gas / rendimiento_gas) * precio_gas)

    # 3. TENENCIA (Promedio 3% anual para combustión. Exento para HEV/PHEV/BEV en centro de México)
    tenencia_mensual = (precio_auto * 0.03) / 12 if tipo_auto == 'Gasolina' else 0

    return costo_energia_mensual, mantenimiento_mensual, tenencia_mensual

def proyectar_costos_acumulados(meses_proyeccion, enganche, mensualidad, costo_energia, 
                                costo_mant, costo_tenencia, meses_credito):
    """
    Genera una lista con el costo total acumulado mes a mes para encontrar el Break-Even.
    """
    acumulado = enganche
    costos_por_mes = []
    
    for mes in range(1, meses_proyeccion + 1):
        pago_auto = mensualidad if mes <= meses_credito else 0
        gasto_total_mes = pago_auto + costo_energia + costo_mant + costo_tenencia
        acumulado += gasto_total_mes
        costos_por_mes.append(acumulado)
        
    return costos_por_mes
