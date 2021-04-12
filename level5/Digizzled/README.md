# Digizzled

## Problem Text

_Had a flag, but it got digizzled. Can you recover it?_

---

Digizzle was a reverse engineering challenge where participants had to reverse-engineer a script to recover the flag.

The [file](digizzle) provided by the organizers was a text file containing disassembled python bytecode, most likely generated using `dis`, a python module.

Along with that was the following output:

```text
-------------------------------------  
      o                  o             
      | o      o         |             
    o-O   o--o   o-o o-o | o-o o-o     
   |  | | |  | |  /   /  | |-' |       
    o-o | o--O | o-o o-o o o-o o       
             |                         
         o--o                          
-------------------------------------  
enter flag: [REDACTED]    
digizzling...  
c5ab05ca73f205ca  
```

The creator of this puzzle was clever in that by giving out python bytecode assembly (text), I could not rely on a decompiler to recreate the original python code, which normally requires binary Python bytecode. Thus began the task of manually decompiling the bytecode assembly.

## The Main Program

These are the first few lines of the bytecode:

```text
  1           0 LOAD_CONST               0 (0)
              2 LOAD_CONST               1 (None)
              4 IMPORT_NAME              0 (re)
              6 STORE_NAME               0 (re)

  2           8 LOAD_NAME                0 (re)
             10 LOAD_METHOD              1 (compile)
             12 LOAD_CONST               2 ('^he2021\\{([dlsz134]){9}\\}$')
             14 CALL_METHOD              1
             16 STORE_NAME               2 (pattern)
```

The bytecode formatting is split into three main columns as follows:

1. The leftmost column is the line number in the original python code.
2. The center column denotes the Python opcode mnemonic and its position in the file.
3. The rightmost column is the symbol, or operand, that the opcode takes.

So, for example:

```text
 4 IMPORT_NAME         0 (re)
 6 STORE_NAME          0 (re)
...
 8 LOAD_NAME           0 (re)
```

In the above case, Python imports the name `re`. The next opcode, `STORE_NAME`, loads the name into memory, effectively bringing the name into scope.

This corresponds to the following python code:

```python
import re
```

where `re` is the name of Python's regular expression library.

The next few opcodes should be quite intuitive. Python loads the name and the method within that name's namespace.

Python's VM is stack-based, which means that all LOAD_* opcodes push a symbol onto the stack. Python's calling convention consists of loading the function's name on the stack, pushing all function parameters onto the stack, and then calling the function via the `CALL_FUNCTION` opcode.

The next few lines of code involve calling into the `re` library's `compile` method, which creates a regex `^he2021\\{([dlsz134]){9}\\}$`. A quick check on regex101.com found that this regex checks that the text it is given has the `he2021{}` wrapper text, and the flag inside the curly brackets. This regex is stored in the variable called `pattern`.

```python
pattern = re.compile('^he2021\\{([dlsz134]){9}\\}$')
```

The next few opcodes are quite interesting:

``` text
  4          18 LOAD_CONST               3 (<code object hizzle at 0x10b3ad270, file "digizzle.py", line 4>)
             20 LOAD_CONST               4 ('hizzle')
             22 MAKE_FUNCTION            0
             24 STORE_NAME               3 (hizzle)
```

Of note here is the `MAKE_FUNCTION` opcode. This obviously means that Python is defining a function. But what is the name of the function?

The answer lies in this opcode: `LOAD_CONST 4 ('hizzle')`. This pushes the constant 'hizzle' onto the stack. The `MAKE_FUNCTION` opcode takes this and defines a function within Python. Thus, these few lines correspond to the following code:

```python
def hizzle():
```

Further down, another function called `smizzle` is also created.

The next few lines consist of printing out the "digizzle" logo as shown in the output above, so they can be ignored.

The next few lines of code after that show that Python is asking the user for input, and storing it in a variable named `s`:

```text
 24         106 LOAD_NAME                6 (input)
            108 LOAD_CONST              15 ('enter flag:')
            110 CALL_FUNCTION            1
            112 STORE_NAME               7 (s)
```

And after that comes the first branch in the code:

```text
 25         114 LOAD_NAME                2 (pattern)
            116 LOAD_METHOD              8 (match)
            118 LOAD_NAME                7 (s)
            120 CALL_METHOD              1
            122 POP_JUMP_IF_FALSE      174
```

So here, we can see that the variable `pattern` is loaded onto the stack, followed by its method `match`, and then the string `s`, which was entered by the user. The `CALL_METHOD` opcode tells us that the `match` method was called on pattern, taking `s` as a parameter. It is, however, the next opcode that is the most interesting.

`POP_JUMP_IF_FALSE` means that the VM should pop the value on top of the stack and jump ahead to another place in memory if `match` evaluates to a falsy value. In this case, it jumps to 174. At location 174 is the following code:

```text
 31     >>  174 LOAD_NAME                5 (print)
            176 LOAD_CONST              18 ('wrong format!')
            178 CALL_FUNCTION            1
            180 POP_TOP
        >>  182 LOAD_CONST               1 (None)
            184 RETURN_VALUE
```

Which evaluates to a call to `print()` to print an error message.

So what we are looking at here is clearly an if-else statement. This evaluates to the following Python code:

```python
if not pattern.match(s):
    print('Wrong format!')
else:
    #do something else
```

So what happens inside the `else` branch? Let's return to where we were in the code.

Immediately after the `POP_JUMP_IF_FALSE` opcode is a call to `print()` to print a small message, then the following code:

```text
 27         132 LOAD_NAME                3 (hizzle)
            134 LOAD_NAME                7 (s)
            136 CALL_FUNCTION            1
            138 STORE_NAME               9 (a)

 28         140 LOAD_NAME                3 (hizzle)
            142 LOAD_NAME                7 (s)
            144 LOAD_CONST               1 (None)
            146 LOAD_CONST               1 (None)
            148 LOAD_CONST              17 (-1)
            150 BUILD_SLICE              3
            152 BINARY_SUBSCR
            154 CALL_FUNCTION            1
            156 STORE_NAME              10 (b)
```

So at first glance we know that we are calling a function, as evidenced by the `CALL_FUNCTION` opcode. We also know that we are calling the `hizzle` function defined earlier on, and storing its return value inside a variable. It also looks like this occurs twice, at 132 and 140. However, the second time looks slightly more complicated. Let's break this down:

```text
            144 LOAD_CONST               1 (None)
            146 LOAD_CONST               1 (None)
            148 LOAD_CONST              17 (-1)
            150 BUILD_SLICE              3
            152 BINARY_SUBSCR
```

So first, three constants are pushed onto the stack: `None`, `None` and `-1`. Following that is the `BUILD_SLICE` opcode. A quick glance at the opcode [reference](http://unpyc.sourceforge.net/Opcodes.html) shows us that `BUILD_SLICE` constructs a Python slice.

A slice in Python is a way of manipulating lists. Using a slice, one can start from and end at a certain index, and step over elements. A slice follows the construct:

```python
item[x:y:z]
```

Where x is the starting index, y is the ending index, and z is the step over. If nothing is placed there, `None` is used. Thus, that is what the three `LOAD_CONST` operations were for. After that, `BUILD_SLICE` is executed with an operand of 3. This means that all three slice operands are used. In this case, starting and ending are `None`, and step over is -1. This means the slice contains all its elements in reverse order. Since `s` is a string (i.e. a list of characters), this means the slice contains `s` in reverse.

The next OPCODE is `BINARY_SUBSCR`. Another quick glance at the reference shows that this opcode indexes into the item on top of the stack. So, to put it all together, this is the Python code it corresponds to:

```python
a = hizzle(s)       # pass in s
b = hizzle(s[::-1]) # pass in s in reverse order
```

After that is fairly simple:

```text
 29         158 LOAD_NAME                5 (print)
            160 LOAD_NAME                4 (smizzle)
            162 LOAD_NAME                9 (a)
            164 LOAD_NAME               10 (b)
            166 CALL_FUNCTION            2
            168 CALL_FUNCTION            1
            170 POP_TOP
            172 JUMP_FORWARD             8 (to 182)
```

This corresponds to a call to `smizzle` passing in `a` and `b`, and then printing out the result.

```python
print(smizzle(a, b))
```

So, now have the overall architecture of the script:

```python
import re

pattern = re.compile('^he2021\\{([dlsz134]){9}\\}$')

def hizzle(s):
    pass # ???

def smizzle(a, b):
    pass # ???

# printing out the logo
# ...

s = input("Enter flag: ")

if not pattern.match(s):
    print('Wrong format!')
else:
    a = hizzle(s)
    b = hizzle(s[::-1])

    print(smizzle(a, b))
```

Great! Now let's see what hizzle and smizzle do.

## Decompiling the functions
