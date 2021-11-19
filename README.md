# py-calc

### Run:
```bash
python main.py
```
```bash
chmod +x main.py
./main.py
```
### Help page:
```bash
python main.py -h
```
### Examples:
```bashV
sh$ ./main.py
> 4*5+2^4
36.0
> 
```
```bash
sh$ ./main.py -d
> 4+4
Debug: lexer returned: '[(1, '4'), (3, '+'), (1, '4'), (0, None)]'
Debug: parser returned: '<interpreter.BinaryOp object at 0x7f0f0b51e790>'
8.0
> 
```
```bash
sh$ ./main.py -c "5*(0+5+0)"
25.0
```
```bash
sh$ ./main.py -dc "3*sin(cos(2))"
Debug: lexer returned: '[(1, '3'), (3, '*'), (4, 'sin'), (2, '('), (4, 'cos'), (2, '('), (1, '2'), (2, ')'), (2, ')'), (0, None)]'
Debug: parser returned: '<interpreter.BinaryOp object at 0x7f7a676a7790>'
-1.2127174615567973
```
### Functions:
```bash
sh$ ./main.py
> fn f(x) = 2*x^3-4*x+12
ok
> f(2)
22.0
> 
```
#### Functions are saved:
```bash
sh$ ./main.py
> fn f(x) = 2*x^3-4*x+12
ok
> ^C
sh$ ./main.py
> f(x)
22.0
> 
```