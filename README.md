Comparador de Costo Total de Propiedad (TCO) de Vehículos 🚗⚡



Esta aplicación web construida con Streamlit permite calcular y comparar el Costo Total de Propiedad (TCO) a lo largo del tiempo para 4 tecnologías de vehículos:



Combustión Interna (Gasolina)



Híbrido Tradicional (HEV)



Híbrido Enchufable (PHEV)



Eléctrico de Batería (BEV)



Estructura del Repositorio



vehiculos-tco-app/

│

├── app.py               # Archivo principal de la aplicación Streamlit (Frontend)

├── tco.py               # Módulo de lógica de negocio y cálculos financieros (Backend)

├── requirements.txt     # Dependencias del proyecto

├── .gitignore           # Archivos ignorados por git

├── LICENSE              # Licencia MIT

└── README.md            # Documentación del proyecto





Características



Cálculo Financiero: Utiliza el sistema de amortización francés (cuota fija) para los créditos automotrices.



Costos Iniciales: Toma en cuenta enganche y comisión por apertura.



Costos Operativos: Calcula el gasto energético mensual basado en el kilometraje anual, precios locales de gasolina y electricidad, y eficiencias específicas de cada motor.



Análisis de Break-Even: Determina en qué mes exacto la inversión extra en una tecnología más limpia/eficiente se recupera gracias a los ahorros operativos frente al auto de gasolina.



Cómo ejecutar el proyecto localmente



Clona el repositorio:



git clone \[https://github.com/tu-usuario/vehiculos-tco-app.git](https://github.com/tu-usuario/vehiculos-tco-app.git)

cd vehiculos-tco-app





Crea un entorno virtual e instala las dependencias:



python -m venv venv

source venv/bin/activate  # En Windows: venv\\Scripts\\activate

pip install -r requirements.txt





Ejecuta la aplicación de Streamlit:



streamlit run app.py

