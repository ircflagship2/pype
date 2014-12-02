pype
====

Bracket-indented Python for Command Line Oneliners:

    ./somecommand | pype 'if _.startswith('py') { print _ }' | ./anothercommand

About
-----
`pype` makes it easy to use python in a typical unix command line pipe. The concept is
easiest to grasp through an example. For the numbers 1 to 5, let's print the square
root of the even numbers.

    $ seq 1 5 | pype 'import math; n = int(_); if n%2==0 { print math.sqrt(n) }'
    1.41421356237
	2.0

- `pype` exposes every input line as the variable `_`.
- You specify a python "function" through a command line argument (`pype 'print whatever(_)'`)
- `pype` executes this function on every input line
- `pype` functions are regular python, but can be indented using curly brackets because useful for command line onelines

Examples
--------
    # list all files/folders in root in uppercase
    $ ls / | pype 'print _.upper()'

    # don't use an alias
    $ ls / | python ~/pype/pype.py 'print _.upper()'

    # print files/folders containing the character 's' in uppercase, otherwise in:
    $ ls / | pype "if 's' in _ { print _.upper() } else { print _.lower() }"

    # do something cummulative using --before and --after. let's count all
    # folders/files containing an s
    $ ls / | pype --before "l = []" --after 'print len(l)' \
        "if 's' in _: l.append(_)"

    # print the properly indented source code executed, together verbose input
    # and output information using the debug flag. also useful to get an idea
    # of how pype works
    $ ls / | pype --before "l = []" --after 'print len(l)' \
        "if 's' in _: l.append(_)" --debug

    # instead of 'print', you may use the included out(obj) (alias of print) 
    # and err(obj) functions for outputting to respectively stdout and stderr.
    # if you prefer, these functions are also aliased as stdout(obj) and
    # stderr(obj)
    $ ls / | pype "if 's' in _ { out(_) } else { err(_) }" > stdout 2>stderr

Install
-------

`pype` is a very short, hacky little script. It has very few dependencies,
which are all available in python 2.6, so hopefully, you can just download
it and run it as-is!

It's recommended to alias pype (alias pype='python PATH_TO/pype.py'), but you
may just as well just use 'python pype.py'.

Here's three different ways to install pype:

**Install with pip**

    pip install pype-cli

**Manual Install**

Download pype to somewhere suitable:

    mkdir ~/pype
    touch ~/.pype
    wget -O ~/pype/pype.py "https://github.com/pype/pype.py"

Add an alias to `.profile`, `.bashrc` or an equivalent user environment file

	echo 'alias pype="python ~/pype/pype.py"' >> .profile

Other details
-------------

Regularily used imports or functions can be added to ~/.pype . This is a
regular python file that will be included in all pype scripts.