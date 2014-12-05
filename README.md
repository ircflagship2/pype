pype
====

*Curly bracket-indented python for command line oneliners:*

```shell
 ./somecommand | pype "if _.startswith('py') { print _ }" | ./anothercommand
```

About
-----
`pype` makes it easy to use python in a typical unix command line pipe. `pype` exposes
each line on `stdin` as the variable `_`, and lets you write a function to manipulate it:

```shell
$ echo "hello world" | pype 'print _.upper()'
HELLO WORLD
```

To make it easier to write one-liners, `pype` allows you to use curly brackets for indentation. 
Let's calculate the square of the even numbers between 1 and 5:

```shell
$ seq 1 5 | pype 'n = int(_); if n%2==0 { print "{0}*{0}={1}".format(n, n*n) }'
2*2=4
4*4=16
```

Install
-------

`pype` is a very short, hacky little script (and is defintely not suitable for production
environments at this point). It has very few dependencies, which are all available in 
python 2.6, so hopefully, you can just download it and run it as-is!

It's recommended to alias pype, i.e. `alias pype='python PATH_TO/pype`, but you
can just as well use `python pype 'my code'`.

**Install with pip**

```
pip install pypecli
```

**Manual Install**

Copy & paste-installer for the brave. Modify `PYPE_INSTALL_PATH` and `PYPE_RC_FILE` as required:

```shell
PYPE_INSTALL_PATH="$HOME/bin" && \
PYPE_RC_FILE="$HOME/.bashrc" && \
mkdir -p "$PYPE_INSTALL_PATH" && \
wget -O "$PYPE_INSTALL_PATH/pype" "https://raw.githubusercontent.com/ircflagship2/pype/master/pype" && \
echo "alias pype=\"python $PYPE_INSTALL_PATH/pype\"" >> $PYPE_RC_FILE && \
source $PYPE_RC_FILE
```

Advanced Functionality and More Examples
----------------------------------------

List all files/folders in `/` in uppercase:

```shell
$ ls / | pype 'print _.upper()'
```

Do the same, without an alias:

```shell
$ ls / | python ~/bin/pype.py 'print _.upper()'
```

Print files/folders containing the character *s* in uppercase, the rest in lowercase:

```shell
$ ls / | pype "if 's' in _ { print _.upper() } else { print _.lower() }"
```

Do something cummulative using `--before` and `--after`. Let's count all
folders/files containing an *s*

```shell
$ ls / | pype --before "l = []" --after 'print len(l)' "if 's' in _: l.append(_)"
```

While `pype` auto-imports a handful of often-used imports, the `--before` argument is 
useful if you need to include additional libraries:

```shell
$ ls / | pype --before "import json" "print json.dumps( { 'stdin' : _, 'upper' : _.upper() } )"
```

Print the properly indented source code executed, together with verbose input
and output information using the `--debug` flag. Also useful to get an idea
of how pype works:

```shell
$ ls / | pype --before "l = []" --after 'print len(l)' "if 's' in _: l.append(_)" --debug
```

Instead of using `print`, you may use the included `out(obj)` (alias of `print`) 
and `err(obj)` functions for outputting to respectively `stdout` and `stderr`.
If you prefer, these functions are also aliased as `stdout(obj)` and `stderr(obj)`.

```shell
$ ls / | pype "if 's' in _ { out(_) } else { err(_) }" >stdout.log 2>stderr.log
```

`pype` trims `_` using `str.rstrip` by default. This is generally easier to work with, as `print`,
`out()` and `err()` will add a newline character to output. You can disable this 
behaviour if you need the stdin input unmodified. You'll likely want to use 
`sys.stdout.write()` and `sys.stderr.write()` instead of `print`, `out` and `err`, as the 
`sys` methods do not add an extra newline.

```shell
$ ls / | pype --no-trim "sys.stdout.write( _.upper() )"
```

Code reuse and defaults
-------------

Regularily used imports or functions can be added to `~/.pype` . This is a
regular python file that will be included in all pype scripts. For instance, adding the 
content below to `~/.pype` will allow you to run 
`ls / | pype 'printtwice( math.sqrt( int(_) ) )` without errors:

```python
import math

def printtwice(out):
	print out
	print out
```

Issues
------

Issues and pull requests are gladly accepted. The biggest known problem is that the conversion
between curly-bracketed and tabular-indented python is entirely untested, and likely to fail for
anything more complex than very simple oneliners, like the ones in these examples.

Contributors
------------

- [Jens Kristian Geyti](http://www.github.com/jkgeyti)
