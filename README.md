# README - Name Variants


Generador ligero de variantes de nombres para recon / OSINT.
Produce iniciales, combinaciones, formatos tipo usuario/email-local y otras variantes útiles para generar wordlists o patrones de búsqueda.


---


## Requisitos
- Python 3.8+ (sin dependencias externas)


---


## Instalación
Clona el repositorio y ejecuta directamente el script:
```bash
git clone https://github.com/<tu_usuario>/name-variants.git
cd name-variants
```


No requiere instalación adicional. Si prefieres, puedes crear un entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate # Linux/macOS
# o
.venv\\Scripts\\activate # Windows
```


---


## Uso básico (CLI)
Genera variantes de un nombre:
```bash
python name_variants.py --name "Pepito Pérez"
```


Salida ejemplo (modo legible):
```
Nombre: Pepito Pérez
Variantes (all):
- pepito perez
- pepitoperez
- pepito
- perez
- pperez
- pepito.perez
- p.perez
- pepito_perez
- pepito-perez
- perez.p
...
```


---


## Otras opciones
| Opción | Descripción |
|--------|--------------|
| `--json` | Muestra la salida en formato JSON. |
| `--max N` | Limita el número total de variantes generadas. |
| `--keep-accents` | Conserva acentos en las variantes. |
| `--case {lower,original,upper}` | Define formato de mayúsculas/minúsculas (por defecto `lower`). |
| `--file nombres.txt` | Lee nombres desde un archivo (uno por línea). |



## Ejemplo de salida








## Ejemplo de salida JSON
```json
{
"Pepito Pérez": {
"groups": {
"full": ["pepito perez"],
"given_sep_family": ["pepito.perez", "pepito_perez", "pepito-perez"]
},
"all": [
"pepito perez",
"pepitoperez",
"pepito",
"perez",
"pperez",
"pepito.perez",
"p.perez"
]
}




