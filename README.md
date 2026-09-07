# Proyecto No. 1 — Analizador Léxico (Regex → AFN → AFD → AFD mínimo)

Universidad del Valle de Guatemala, Facultad de Ingeniería.

Programa que recibe una expresión regular `r` y una cadena `w`, y determina
si `w ∈ L(r)`, pasando por Shunting Yard, construcción de Thompson,
construcción de subconjuntos, minimización de AFD y simulación.

## Instalación

Requiere Python 3.11 o superior.

```
python -m venv venv
```

Activar el entorno virtual:
- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- macOS / Linux: `source venv/bin/activate`

Instalar dependencias:
```
pip install -r requirements.txt
```

También se necesita el binario de Graphviz instalado en el sistema (además
de la librería de Python) para poder renderizar las imágenes PNG:
- **Windows**: instalador desde https://graphviz.org/download/ (agregarlo al PATH).
- **macOS**: `brew install graphviz`
- **Linux (Debian/Ubuntu)**: `sudo apt install graphviz`

Verificar instalación:
```
dot -V
```

## Uso

```
python main.py <archivo_de_regex.txt>
```

Por cada línea del archivo de entrada (una expresión regular por línea), el
programa genera las imágenes del AFN, AFD y AFD minimizado en `output/`, y
luego pide por consola una cadena `w` para evaluarla contra los tres
autómatas.

## Estructura del proyecto

```
main.py                  # orquesta el flujo completo, lee el archivo, hace input()
shunting_yard.py         # tokenización + infix a postfix
thompson.py               # construcción del AFN desde postfix
subset_construction.py   # AFN -> AFD
minimization.py          # minimización del AFD
simulator.py              # simulación de AFN/AFD sobre una cadena w
graph_renderer.py        # generación de imágenes PNG con graphviz para AFN/AFD/AFD-min
```

## Alcance de operadores soportados

- `|` unión
- `*` cierre de Kleene
- `+` cierre positivo
- `?` opcional
- `.` wildcard (unión de todos los símbolos del alfabeto detectado en esa
  expresión específica, más el propio carácter `.`)
- concatenación implícita
- `()` agrupación
- `\` escape de literales

El símbolo interno de épsilon usado en el AFN es `$`.

