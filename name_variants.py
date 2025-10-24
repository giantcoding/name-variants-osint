"""
Generador sencillo de variantes de nombres (para proyectos de recon y OSINT).

Cómo usar:
  - Importar la función `generate_variants(name, max_items=None, options=None)` desde este archivo.
  - Ejecutable CLI: `python name_variants.py --name "Pepito Pérez" --json`

Características:
  - Normaliza acentos y mayúsculas.
  - Genera variantes comunes: iniciales, separadores (., _, -), solo nombre, solo apellido,
    inicial+apellido, apellido+inicial, concatenados, formatos tipo usuario, email local,
    abreviaciones, y algunas transformaciones útiles.
  - Devuelve un dict con agrupaciones y una lista única con todas las variantes.

Sin dependencias externas (solo stdlib).
"""

from __future__ import annotations
import argparse
import json
import unicodedata
import re
from typing import List, Dict, Set, Optional

SEPARATORS = ['.', '_', '-', '']


def _strip_accents(s: str) -> str:
    """Quita acentos y diacríticos y normaliza espacios."""
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", ' ', s).strip()
    return s


def _clean_token(tok: str) -> str:
    tok = _strip_accents(tok)
    tok = tok.replace("'", "")  # quitar apóstrofes
    tok = tok.strip()
    return tok


def _split_name(name: str) -> List[str]:
    """Devuelve tokens del nombre (nombre(s) y apellidos).

    Heurística simple: split por espacios y eliminar tokens vacíos.
    """
    name = name.strip()
    if not name:
        return []
    tokens = [t for t in re.split(r"\s+", name) if t]
    return [_clean_token(t) for t in tokens]


def _initial(token: str) -> str:
    return token[0] if token else ''


def generate_variants(name: str, max_items: Optional[int] = None, options: Optional[Dict] = None) -> Dict[str, List[str]]:
    """Genera variantes para un nombre completo.

    Devuelve un dict con keys:
      - groups: mapping de categoria -> lista
      - all: lista única con todas las variantes (ordenada por aparición)

    Parámetros:
      - name: cadena con el nombre completo (ej: "Pepito Pérez")
      - max_items: si se pasa, limita el número total de variantes devueltas en `all`.
      - options: diccionario para activar/desactivar comportamientos (no obligatorio).

    opciones válidas (keys):
      - keep_accents (bool): si True mantiene acentos. Default False.
      - case ("lower"|"original"|"upper"): cómo devolver las variantes. Default "lower".
    """
    if options is None:
        options = {}
    keep_accents = options.get('keep_accents', False)
    case = options.get('case', 'lower')

    tokens = _split_name(name)
    if not tokens:
        return {'groups': {}, 'all': []}

    # heurística: asumimos último token = apellido principal
    if len(tokens) == 1:
        nombres = [tokens[0]]
        apellidos = []
    else:
        nombres = tokens[:-1]
        apellidos = [tokens[-1]]

    first = nombres[0] if nombres else ''
    last = apellidos[0] if apellidos else ''

    groups: Dict[str, List[str]] = {}
    produced: List[str] = []
    seen: Set[str] = set()

    def _add(cat: str, val: str):
        v = val if keep_accents else _strip_accents(val)
        if case == 'lower':
            v = v.lower()
        elif case == 'upper':
            v = v.upper()
        # else original capitalization left as-is
        if v and v not in seen:
            groups.setdefault(cat, []).append(v)
            produced.append(v)
            seen.add(v)

    # 1) Formas completas
    full = ' '.join(tokens)
    _add('full', full)
    _add('compact', full.replace(' ', ''))

    # 2) (nombre(s) y apellido)
    for t in nombres:
        _add('given', t)
    for t in apellidos:
        _add('family', t)

    # 3) Inicialess
    initials = ''.join(_initial(t) for t in nombres + apellidos)
    if initials:
        _add('initials_concat', initials)
    if nombres:
        _add('given_initials', ''.join(_initial(n) for n in nombres))
    if apellidos:
        _add('family_initial', _initial(last))

    # 4) initial + surname and surname + initial with separators
    for sep in SEPARATORS:
        if nombres and apellidos:
            left = _initial(first) + sep + last
            right = last + sep + _initial(first)
            _add('initial_sep_surname', left)
            _add('surname_sep_initial', right)
        # also for full first name + sep + initial
        if nombres:
            _add('given_sep_initial', first + sep + _initial(first))

    # 5) dot/underscore/hyphen combos between given and family
    for sep in SEPARATORS:
        if nombres and apellidos:
            _add('given_sep_family', first + sep + last)
            # multiple given names
            if len(nombres) > 1:
                _add('given_full_sep_family', ' '.join(nombres) + sep + last)

    # 6) concatenaciones y usernames
    if nombres and apellidos:
        _add('concat_gf', first + last)
        _add('concat_fg', last + first)
        _add('email_local_1', first + '.' + last)
        _add('email_local_2', _initial(first) + last)
        _add('email_local_3', first + _initial(last))

    # 7) variaciones con iniciales intermedias (si las hubiese)
    if len(nombres) > 1:
        mid_initials = ''.join(_initial(n) for n in nombres[1:])
        _add('given_middle_initials', first + ''.join(n for n in nomes_to_str(nombres[1:])))
        # also first+midinitial+last
        _add('fm_initials_l', first + ''.join(_initial(n) for n in nombres[1:]) + last)

    # 8) apellido solo con prefijos comunes
    if last:
        _add('surname_dot', last + '.')
        _add('surname_with_initial', last + _initial(first))

    # 9) Formas con punto en una sola palabra
    if nombres and apellidos:
        _add('initial_dot_surname', _initial(first) + '.' + last)
        _add('initial_underscore_surname', _initial(first) + '_' + last)

    # 10) reserva tokens individualmente y en mayúsculas
    for t in tokens:
        _add('token', t)

    # Crear una lista combinada de "todos los nombres"
    all_list = produced.copy()
    if max_items is not None:
        all_list = all_list[:max_items]

    return {'groups': groups, 'all': all_list}


# Utilidades utilizadas arriba

def nomes_to_str(lst: List[str]) -> List[str]:
    """Aux: convierto lista a lista de strings (defensa de tipo)."""
    return [str(x) for x in lst]


def _cli():
    parser = argparse.ArgumentParser(description='Generador de variantes de nombres.')
    parser.add_argument('--name', '-n', help='Nombre completo (ej: "Pepito Pérez").')
    parser.add_argument('--file', '-f', help='Fichero con nombres, una línea por nombre.')
    parser.add_argument('--json', action='store_true', help='Salida en JSON (por defecto).')
    parser.add_argument('--max', type=int, help='Máximo de variantes a mostrar (total).')
    parser.add_argument('--keep-accents', action='store_true', help='Mantener acentos en las variantes.')
    parser.add_argument('--case', choices=['lower', 'original', 'upper'], default='lower', help='Formato de mayúsculas/minúsculas.')

    args = parser.parse_args()
    names = []
    if args.name:
        names.append(args.name)
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as fh:
            for l in fh:
                l = l.strip()
                if l:
                    names.append(l)
    if not names:
        parser.error('Se requiere --name o --file')

    out = {}
    opts = {'keep_accents': args.keep_accents, 'case': args.case}
    for nm in names:
        out[nm] = generate_variants(nm, max_items=args.max, options=opts)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        # formato simple legible
        for nm, v in out.items():
            print(f'Nombre: {nm}')
            print('Variantes (all):')
            for x in v['all']:
                print('  -', x)
            print()  


if __name__ == '__main__':
    _cli()

