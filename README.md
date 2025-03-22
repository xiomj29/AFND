# Simulador de Autómatas Finitos Deterministas (AFD) y No Deterministas (NFA)

Este proyecto es un simulador de autómatas finitos deterministas (AFD) y no deterministas (NFA) con una interfaz gráfica desarrollada en Python utilizando `tkinter`. El simulador permite definir, simular y convertir autómatas, así como realizar análisis de cadenas y operaciones relacionadas con lenguajes formales.

---

## Características Principales

1. **Definición de Autómatas**:
   - Crear y modificar autómatas (AFD y NFA).
   - Añadir estados, transiciones y definir estados iniciales y finales.
   - Soporte para transiciones lambda (ε) en NFA.

2. **Simulación de Autómatas**:
   - Validar cadenas de entrada en un AFD o NFA.
   - Visualizar los pasos de la simulación, incluyendo estados activos y ramificaciones.

3. **Conversión entre Autómatas**:
   - Convertir un NFA a un AFD utilizando el algoritmo de subconjuntos.
   - Eliminar transiciones lambda de un NFA.

4. **Herramientas Adicionales**:
   - Calcular subcadenas, prefijos y sufijos de una cadena.
   - Generar la cerradura de Kleene y positiva de un alfabeto.

5. **Importación y Exportación**:
   - Cargar autómatas desde archivos en formato `.jff` (JFLAP) o `.afd` (formato propio).
   - Guardar autómatas en formato `.afd`.

6. **Pruebas Múltiples**:
   - Validar múltiples cadenas desde un archivo de texto y generar un informe.

---

## Requisitos

- **Python 3.x**: Asegúrate de tener Python instalado en tu sistema.
- **Bibliotecas**:
  - `tkinter`: Para la interfaz gráfica (viene incluida con Python).
  - `xml.etree.ElementTree`: Para manejar archivos `.jff`.
  - `json`: Para manejar archivos `.afd`.

---

## Instrucciones de Uso

1. **Clonar el Repositorio**:
   Si tienes el código en un repositorio, clónalo en tu máquina local:
   ```bash
   git clone https://github.com/xiomj29/AFND.git
   cd AFND
   python3 practica3.py
## Interfaz Gráfica

### Pestañas Principales

1. **Pestaña de Definición**:
   - Aquí puedes definir los estados y transiciones del autómata.
   - Añade estados, marca uno como inicial y otro como final.
   - Define transiciones entre estados.

2. **Pestaña de Simulación**:
   - Valida cadenas de entrada en el autómata.
   - Observa los pasos de la simulación, incluyendo estados activos y ramificaciones.

3. **Pestaña de Herramientas**:
   - Realiza operaciones como calcular subcadenas, prefijos y sufijos.
   - Genera la cerradura de Kleene y positiva de un alfabeto.

### Cargar y Guardar Autómatas

- **Cargar Autómata**:
  - Usa el botón "Cargar Autómata" para importar autómatas desde archivos `.jff` (JFLAP) o `.afd` (formato propio).
  
- **Guardar Autómata**:
  - Usa el botón "Guardar Autómata" para exportar el autómata actual a un archivo `.afd`.

### Convertir NFA a DFA

- Si has cargado un NFA, puedes convertirlo a un DFA usando el botón **"Convertir NFA a DFA"**.
- El DFA resultante se mostrará en la tabla de transiciones.

### Validar Múltiples Cadenas

- Carga un archivo de texto con cadenas y usa la función **"Validar Múltiples Cadenas"** para obtener un informe de los resultados.

---

## Ejemplos de Uso

### Definir un AFD

1. En la **pestaña de definición**, añade estados y marca uno como inicial y otro como final.
2. Añade transiciones entre estados.
3. Guarda el autómata en un archivo `.afd`.

### Simular una Cadena

1. En la **pestaña de simulación**, ingresa una cadena y haz clic en **"Validar"**.
2. Observa los pasos de la simulación en la sección **"Simulación paso a paso"**.

### Convertir un NFA a DFA

1. Carga un NFA desde un archivo `.jff`.
2. Haz clic en **"Convertir NFA a DFA"**.
3. Observa el DFA resultante en la tabla de transiciones.

### Calcular Subcadenas

1. En la **pestaña de herramientas**, ingresa una cadena y haz clic en **"Calcular"**.
2. Observa las subcadenas, prefijos y sufijos generados.

---

## Estructura del Código

- **`State`**: Clase que representa un estado en un autómata.
- **`AFD`**: Clase que implementa un autómata finito determinista.
- **`NFA`**: Clase que implementa un autómata finito no determinista.
- **`AFDSimulator`**: Clase principal que maneja la interfaz gráfica y la lógica del simulador.

---
