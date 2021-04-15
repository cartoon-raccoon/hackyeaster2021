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

Python's VM is stack-based, which means that opcodes push an item onto the stack, and other opcodes pop items off the stack for use in their operations. Python's calling convention consists of loading the function's name on the stack, pushing all function parameters onto the stack, and then calling the function via the `CALL_FUNCTION` opcode. This pops all the parameters up to the function name, then calls the function with the name pushed onto the stack.

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

So first, three constants are pushed onto the stack: `None`, `None` and `-1`. Following that is the `BUILD_SLICE` opcode. A quick glance at the opcode [reference](http://unpyc.sourceforge.net/Opcodes.html) shows us that `BUILD_SLICE` constructs a Python slice operation.

A slice in Python is a way of manipulating lists. Using a slice, one can start from and end at a certain index, and step over elements. A slice follows the construct:

```python
item[x:y:z]
```

Where x is the starting index, y is the ending index, and z is the step over. If nothing is placed in its position, `None` is used. Thus, that is what the three `LOAD_CONST` operations were for: to load slice operands. After that, `BUILD_SLICE` is executed with an operand of 3. This means that all three slice operands are popped off the stack and used. In this case, starting and ending are `None`, and step over is -1. This means the slice contains all its elements in reverse order. Since `s` is a string (i.e. a list of characters), this means the slice contains `s` in reverse.

The next OPCODE is `BINARY_SUBSCR`. Another quick glance at the reference shows that this opcode pops the top two items off the stack, applying one to the other. So, in this case, the slice operation is applied to the string `s`.

So, to put it all together, this is the Python code it corresponds to:

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

The bytecode assembly for the functions can be found near the bottom of the file:

```text
Disassembly of <code object hizzle at 0x10b3ad270, file "digizzle.py", line 4>:
  5           0 LOAD_CONST               1 (13)
              2 STORE_FAST               1 (s1)

  6           4 LOAD_CONST               2 (37)
              6 STORE_FAST               2 (s2)

  7           8 SETUP_LOOP              52 (to 62)
             10 LOAD_GLOBAL              0 (range)
             12 LOAD_GLOBAL              1 (len)
             14 LOAD_FAST                0 (s)
...
```

Back at the start of the file, we saw the main program execute the `MAKE_FUNCTION` opcode. This causes the VM to jump to the location of the `hizzle` code object and compile the code it finds there.

Let's look at what each function does.

### `hizzle`

The function begins with the following bytecode:

```text
  5           0 LOAD_CONST               1 (13)
              2 STORE_FAST               1 (s1)

  6           4 LOAD_CONST               2 (37)
              6 STORE_FAST               2 (s2)
```

This seems obvious enough: Constant values are pushed onto the stack, and are stored in memory.

This evaluates to the following code:

```python
s1 = 13
s2 = 37
```

The next few lines are where it gets interesting:

```text
  7           8 SETUP_LOOP              52 (to 62)
             10 LOAD_GLOBAL              0 (range)
             12 LOAD_GLOBAL              1 (len)
             14 LOAD_FAST                0 (s)
             16 CALL_FUNCTION            1
             18 CALL_FUNCTION            1
             20 GET_ITER
        >>   22 FOR_ITER                36 (to 60)
             24 STORE_FAST               3 (n)
```

There's some opcodes we've never seen before, but they seem pretty self-explanatory. But first, some more info on the Python VM.

The Python VM maintains more than one stack. Its main stack consists of the stack frames of all the functions currently running. The base of the stack is the stack frame of the `__main__` function, which is the entry point of every Python program.

Within each stack frame, Python also maintains an evaluation frame. This allows Python to keep track of stack variables.

Lastly, Python maintains a block stack. This tracks the level of nesting Python is at. Every time code execution enters a block, like a `try except` block, `if else` block or a loop, a new block is pushed onto the block stack.

With that in mind, let's look at the bytecode.

The first opcode is the `SETUP_LOOP` opcode. This tells Python to push a loop block onto the block stack. Now, we know that we are setting up for a loop.

The next two opcodes call the global names `range` and `len`. To any experienced Python user, they will know that these two names refer to two of Python's built in functions. `range` creates an iterable object from a given integer value. `len` gets the length of any iterable or mappable object, like a list, string, or dictionary.

After this, the opcode LOAD_FAST appears. This just loads the name `s` and pushes it onto the stack. This is followed by two `CALL_FUNCTION` opcodes. At this point, we can be fairly sure we are calling `len(s)` within `range()`.

The next two opcodes set up the iterator for the loop. `GET_ITER` converts the item on top of the stack (TOS) into an iterator, which is consumed by the next opcode, `FOR_ITER`. This opcode tells Python that the item at the top of the stack is an iterator, so it calls another inbuilt function `next()` on the TOS. Also, `FOR_ITER`'s operands show that it goes to location 60. What's just before location 60?

```text
             58 JUMP_ABSOLUTE           22
        >>   60 POP_BLOCK
```

We can see that the VM does an unconditional jump back to location 22, which is the location of the `FOR_ITER` opcode! Right below that is the `POP_BLOCK` opcode, which removes the loop block from the block stack.

The final opcode stores the TOS into the variable `n`. This value is the return value of the `next()` function call.

So, we can infer that this block of bytecode corresponds to the following Python code:

```python
for n in range(len(s)):
    pass # ???
```

So, what's inside the loop?

After the initial loop setup is the following bytecode:

```text
  8          26 LOAD_FAST                1 (s1)
             28 LOAD_GLOBAL              2 (ord)
             30 LOAD_FAST                0 (s)
             32 LOAD_FAST                3 (n)
             34 BINARY_SUBSCR
             36 CALL_FUNCTION            1
             38 BINARY_ADD
             40 LOAD_CONST               3 (65521)
             42 BINARY_MODULO
             44 STORE_FAST               1 (s1)
```

Nothing we haven't seen before. Let's go over this quickly.

- We push `s1` onto the stack.
- We load the global name `ord`. This corresponds to the `ord()` function, which takes a character and returns its representing integer.
- We push `s` and `n` onto the stack.
- We execute `BINARY_SUBSCR`, which performs the indexing operation, indexing into the `n`th element of `s`.
- We call `ord()` on the result of the `BINARY_SUBSCR` operation.
- At this point, the return value of `ord(s[n])` is TOS, and just below it is the value of `s1` as TOS1. Next up is the opcode `BINARY_ADD`, which does exactly what it says: it pops TOS and TOS1 off the stack and adds them together, pushing the result onto the stack.
- We push the constant 65521 onto the stack. At this point, 65521 is TOS and the result of the add operation is TOS1.
- We perform `BINARY_MODULO` on TOS and TOS1, pushing the result back on the stack.
- We store TOS back into s1.

That was a lot, but we aren't done yet. Right after that is this bytecode:

```text
  9          46 LOAD_FAST                1 (s1)
             48 LOAD_FAST                2 (s2)
             50 BINARY_MULTIPLY
             52 LOAD_CONST               3 (65521)
             54 BINARY_MODULO
             56 STORE_FAST               2 (s2)
```

You know the drill. Let's do this.

- We push `s1` and `s2` onto the stack.
- We execute `BINARY_MULTIPLY`, which multiplies TOS and TOS1 together (duh). In this case, `s1` and `s2` are the operands.
- We push the constant 65521 onto the stack (again!)
- We perform `BINARY_MODULO` (again!)
- We then store the result into `s2`.

Once we finish the loop (i.e. `range(len(s))` returns `None`), we exit and pop the block off the stack.

Whew! We can now show what the for loop looks like:

```python
for n in range(len(s)):
    s1 = (s1 + ord(s[n])) % 65521
    s2 = (s1 * s2) % 65521
```

To round off the function, right after the loop is the following bytecode:

```text
 10     >>   62 LOAD_FAST                2 (s2)
             64 LOAD_CONST               4 (16)
             66 BINARY_LSHIFT
             68 LOAD_FAST                1 (s1)
             70 BINARY_OR
             72 RETURN_VALUE
```

This is the ending bit of the function, and it's nothing we haven't seen.

- We push `s2` onto the stack.
- We push the constant 16 onto the stack.
- We perform the `BINARY_LSHIFT` operation, which shifts `s2` bitwise left by 16.
- We push `s1` onto the stack. At this point, `s1` is TOS, and the result of the bitshift operation is TOS1.
- We perform `BINARY_OR`, which performs bitwise OR on TOS and TOS1.
- We return the value and exit the function.

Great! We now have a pretty good idea of what `hizzle` looks like:

```python
def hizzle(s):
    s1 = 13
    s2 = 37

    for n in range(len(s)):
        s1 = (s1 + ord(s[n])) % 65521
        s2 = (s1 * s2) % 65521
    
    return (s1 << 16) | s1
```

Nice! Now let's look at `smizzle`.

### `smizzle`

Compared to `hizzle`, `smizzle` is downright simple. The entire function is the following bytecode:

```text
Disassembly of <code object smizzle at 0x10b3ad9c0, file "digizzle.py", line 12>:
 13           0 LOAD_GLOBAL              0 (format)
              2 LOAD_FAST                0 (a)
              4 LOAD_CONST               1 ('x')
              6 CALL_FUNCTION            2
              8 LOAD_GLOBAL              0 (format)
             10 LOAD_FAST                1 (b)
             12 LOAD_CONST               1 ('x')
             14 CALL_FUNCTION            2
             16 BINARY_ADD
             18 RETURN_VALUE
```

Let's give it the usual treatment.

- We load the global name `format`, corresponding to the Python builtin `format`, which formats a given string according to user-specified parameters.
- We load the `a` onto the stack.
- We load the constant string `'s'` onto the stack.
- We execute `CALL_FUNCTION`, which calls `format()` on TOS and TOS1.

And then we do it all over again for `b`.

Finally we call `BINARY_ADD` on the results of both `format()` calls. In Python, this performs string concatenation, joining the two strings together. This result is then returned.

So now, we can see what `smizzle` looks like:

```python
def smizzle(a, b):
    return format(a, 'x') + format(b, 'x')
```

A quick glance at the Python documentation shows that `format()`, when passed 'x' as its format parameter, returns the hexadecimal notation of its first parameter. So, for example, `format(255, 'x')` returns `'ff'`.

Amazing! We can now put together the entire script!

```python
import re

pattern = re.compile('^he2021\\{([dlsz134]){9}\\}$')

def hizzle(s):
    s1 = 13
    s2 = 37

    for n in range(len(s)):
        s1 = (s1 + ord(s[n])) % 65521
        s2 = (s1 * s2) % 65521
    
    return (s1 << 16) | s1

def smizzle(a, b):
    return format(a, 'x') + format(b, 'x')

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

Great! Now let's go find that flag!

## Finding the Flag

To find the flag, let's go back to the original output provided:

```text
c5ab05ca73f205ca  
```

From the reconstructed script, we can see that the output is a concatenation of two numbers: `hizzle(flag)` and `hizzle(flag[::-1])`. The first thought from here would be to take the first half of the output and work backwards through the `hizzle()` function, but there's a problem: some of the operations in `hizzle` are lossy; that is, for an operation `a <operation> b = c`, given `a` and `c`, it is impossible to find `b`. In particular, bitwise OR and modulo functions are borderline impossible to do. `hizzle()` in essence is a hash function: It easily performs a function one way, but is very difficult to do backwards.

Of course, however, there is another way. Let's take a look at the regex given to check whether the flag is in the correct format:

```text
^he2021\\{([dlsz134]){9}\\}$
```

The characters `^` and `$` on the front and back of the regex are for asserting that the enclosed text is all that is given and matches completely. After that of course, we see the requisite format of `he2021{<flag>}` that all flags must have. But where we can find a clue as to the flag is inside the curly brackets. Inside is this rule:

```text
([dlsz134]){9}
```

This means that for a pattern to match this rule, it can only contain characters that appear in the list `[dlsz134]`, and the string must be exactly 9 characters long.

So now we have some pretty big clues as to the identity of our flag. How are we going to find it? With good old fashioned brute-forcing, of course!

To help us find every permutation of the characters `[dlsz134]`, we can use the Python `itertools` library, specifically its `product()` function. This takes a list, the length of each permutation, and returns an iterator over every permutation of the list.

So, we can now bruteforce this by modifying the script like so:

```python
for s in product("dlsz134", repeat=9):
    string = "he2021{" + "".join(s) + "}"
    a = hizzle(string)
    b = hizzle(string[::-1])

    final = smizzle(a, b)

    if final == "c5ab05ca73f205ca":
        print(final, string)
```

This iterates over every result in `product("dlsz134")`, formats it into the flag format string, and feeds it into `hizzle()` and `smizzle()`. It then compares the result to the given output string, and prints out any match.

And now, we can find our flag!

```text
$ python digizzle.py
c5ab05ca73f205ca he2021{d1s4zzl3d}
```

---
*Flag:* `he2021{d1s4zzl3d}`
