# py-calc

### Suoritus:
```bash
$ python main.py
```
Tai:
```bash
$ chmod +x main.py
$ ./main.py
```
### Liput:
```bash
python main.py -h
```
- `-c [rivi]` antaa suorittaa `[rivi]` suoraan
- `-h` näyttää kytkimet
- `-d` debug tila
- `-p` format tila



### Esimerkkejä:
```bash
$ ./main.py
> 4*5+2^4
36.0
> 
```
```bash
$ ./main.py -d
> 4+4
Debug: lexer returned: '[(1, '4'), (3, '+'), (1, '4'), (0, None)]'
Debug: parser returned: '<interpreter.BinaryOp object at 0x7f0f0b51e790>'
8.0
> 
```
```bash
$ ./main.py -c "5*(0+5+0)"
25.0
```
```bash
$ ./main.py -dc "3*sin(cos(2))"
Debug: lexer returned: '[(1, '3'), (3, '*'), (4, 'sin'), (2, '('), (4, 'cos'), (2, '('), (1, '2'), (2, ')'), (2, ')'), (0, None)]'
Debug: parser returned: '<interpreter.BinaryOp object at 0x7f7a676a7790>'
-1.2127174615567973
```
```bash
$ ./main.py -cf "5*5+3"
(((5.0)*(5.0))+(3.0))
```



#### Toiminta:
Ohjelma syöttää ensiksi merkkijonon `lex` funktiolle `lexer.py` moduulissa. Se käy merkkijonon läpi ja tuottaa jonon eri tokeneita. Ne voi olla numeroita, tekstiä, sulkeita, numerooperaattoreita, pilkkuja tai '=' merkkejä.

Seuraavaksi tokenijono syötetään `parse` funktioon `parser.py` moduulissa. Se käy läpi tokenijonon yrittäen kerätä Abstract Syntax Tree (AST). Se alkaa `stmt` parserista, joka voi olla joko `fn_impl` tai `expr`, joista `fn_impl` on priorisoitu. `fn_impl` parseri yrittää kerätä tokenijonosta järjestyksessä `fn`, funktion nimen, funktion parametrit (joita voi olla 0 tai useampi), '=' merkki ja lopuksi `expr`. `expr` puolestaan kerää niin monta plus tai miinuslaskua kuin mahdollista muodossa `term` + `+`/`-` + `term`. `term` kerää samalla tavalla niin monta kerto tai jakolaskua kuin mahdollista muodossa `atom` + `*`/`/` + `atom`. `atom` lähes samalla tavalla mutta oikealta vasemmalle kerää niin monta potenssilaskua kuin mahdollista `factor` + `^` + `factor`. `factor` on hieman monimutkaisempi, se yrittää järjestyksessä yhtä:
- `+`/`-` + `factor`
	Rekursiivisesti kerää kaikki etumerkit. Esim: `- - - - 4`
- `num`
	Kerää numeron
- `(` + `expr` + `)`
	Kerää sulkeiden ympäröimän `expr`. Esim: `5+(3*x+4)`
- `fn_call`
	Kerää funktion kutsun ja sen argumentit: Esim: `sin(0.5)`
- `const`
	Kerää vakion nimen: Esim `pi * 2`

AST kerättyä se suoritetaan tulkilla. Se käy rekursiivisesti läpi kaikki sen AST:n osat. Esimerkiksi (ei mikään toimiva esimerkki): `BinaryOp('x', '+', BinaryOp('4', '*', 'y'))` käy ensin kohdan `x+` jonka jälkeen suorittaa `4*y` jonka arvo palautetaan ja lasketaan `x+4*y`.

#### Sisään rakennetut vakiot:
`pi`, `e`, `i`
#### Sisään rakennetut funktiot:
`sin(x)`, `cos(x)`, `tan(x)`, `round(x)`

### Funktiot:
```bash
$ ./main.py
> fn f(x) = 2*x^3-4*x+12
ok
> f(2)
22.0
> 
```
```bash
$ ./main.py
> fn sqrt(x) = x^(1/2)
ok
> fn g(a,b) = sqrt(a^2 + b^2)
ok
> g(3,4)
5.0
> 
```
```bash
$ fn x() = 54
ok
> x
54.0
> 
```
#### Funktiot tallennetaan:
```bash
$ ./main.py
> fn f(x) = 2*x^3-4*x+12
ok
> ^C
$ ./main.py
> f(x)
22.0
> 
```