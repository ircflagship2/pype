#!/usr/bin/env python 

""" Pype: Python for Command Line Oneliners

This script makes it simple to use python in a typical unix command line pipe.
Provide python code in command line arguments (pype 'my code here'), that will
be executed for each line on stdout, available as the variable _ .

Pype allows you to use curly brackets as indentation, making it simpler to use
in a terminal setting.

It's recommended to alias pype (alias pype='python PATH_TO/pype.py'), but you
may just as well just use 'python pype.py'.

Regularily used imports or functions can be specified in ~/.pype . This is a
regular python file that will be included in all pype scripts.

Examples:
    # list all files/folders in root in uppercase
    $ ls / | pype 'print _.upper()'

    # don't use an alias
    $ ls / | python ~/pype/pype.py 'print _.upper()'

    # print files/folders containing the character 's' in uppercase:
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

"""

__author__ = "Jens Kristian Geyti"
__license__ = "MIT"
__version__ = "1.0.1"

# besides the imports used by this script itself, these are
# regularily used imports useful for the eval'ed user code.
# for instance, making exit(int) avilable, so end user won't
# have to 'import sys; sys.exit(0)'.
import datetime, os, pprint, re, sys, time, math
from sys import exit
from optparse import OptionParser # use over argparse for python 2.6 support

# include user code (imports and functions). it's just a python file.
if os.path.isfile(os.path.expanduser('~/.pype')):
    with open(os.path.expanduser('~/.pype')) as f:
        exec(f.read())

# predefined helper methods available to the user.
def out(output):    
    # this is basically the same a print, but it's included for completeness
    sys.stdout.write("{0}\n".format(output))

def stdout(output): return out(output) # out alias

def err(output):
    sys.stderr.write("{0}\n".format(output)) 

def stderr(output): err(output) # err alias

# put as much code as possible in a 'hidden' class, so as little as possible 
# will pollute the user's namespace
class __pypecls__:

    # indent one or more lines
    def indent(self, lines, tabs):
        return "\n".join([(tabs*"    ") + line for line in lines.split("\n")])

    # create the optparse argument parser
    def parse_args(self):        
        # optionparser that preserves newlines
        class MyParser(OptionParser):
            def format_description(self, formatter):
                return self.description            

        parser = MyParser(usage="pype [options] [code ...]", 
                          version="pype " + __version__,
                          description="Code:".ljust(24) + 
            "python code to execute on each line from stdin,\n" +
            " "*24 + "available as the variable _. use curly braces for\n" + 
            " "*24 + "indentations. use print or out(obj) for printing to\n" +
            " "*24 + "stdout, err(obj) for printing to stderr, and\n" +
            " "*24 + "exit() (imported from sys) for exit codes")
        
        parser.add_option('-b', '--before', 
            dest='before', 
            help='code to execute before processing stdin')
        parser.add_option('-a', '--after', 
            dest='after', 
            help='code to execute after processing stdin')
        parser.add_option('-d', '--debug', dest='debug', 
            help='debug output. Shows source and every input/output ' + 
                 'processed)', 
            action='store_true', 
            default=False)
        parser.add_option('--no-trim', 
            dest='stripnewlines', 
            action='store_false', 
            default=True, 
            help='newlines at the end of input lines are stripped by default '+ 
                 'for better compatability with "print". Set this flag to ' + 
                 'disable this behaviour.')

        return parser.parse_args() 

    def addchar(self, whitespace_source, char):        
        return whitespace_source

    def parse_source(self, bracket_source):

        # create a 3-character wide sliding window generator
        # as the "current" element of the sliding window is always the middle 
        # one, we'll add 1 character of whitespace on each side of the source, 
        # so the first and last character are processed correctly.
        bracket_source_chars = [''] + list(bracket_source) + ['']
        sliding_window = [bracket_source_chars[i:i+3] for i in \
                xrange(len(bracket_source))]

        # the input (bracketed) source is converted to valid python, and 
        # continiously added to this var. in the end, this source is returned, 
        # and then execed
        whitespace_source = ""

        # we parse the input (bracketed) source char by char (with one char 
        # lookbehind & ahead. as we go along, we can be in various 'states' 
        # (think AST). The following variables constitues these various states.

        # currently in a quoted string?
        in_quote = False

        # about to declare a variable (right after '=' char)?
        in_declaration = False

        # are we inside a paranthesis/bracket/curly braces?
        in_paranthesis = False
        in_square_brackets = False
        in_dict = False
        last_was_newline = False

        # indentation level. used when prepending output source with whitespace
        level = 0

        def indent_if_needed(chars):            
            if chars.endswith("\n"):
                chars += "    "*level
            return chars

        # turn the bracketed python code into proper whitespace-indented python
        # code by iterating over the sliding window, one character at a time. 
        for prevchar,char,nextchar in sliding_window:

            # by default, and in most cases, the char to add to the indented
            # code is the same as the input char. this MAY however be changed 
            # in certain situations by the rules below:
            chars_to_add = char

            # first check if we're working with whitespace around newlines that 
            # needs to be stripped
            if last_was_newline:
                if char == ' ':
                    # skip this whitespace
                    continue
                else:
                    last_was_newline = False

            # check if we're in "escape mode", i.e. previous character was an
            # escape character.
            if prevchar == "\\":
                # If so, the current character can never affect the 
                # indentation, so make sure none of the other rules are matched
                whitespace_source += indent_if_needed(char)
            
            # check if we're entering or leaving a quoted string. brackets in
            # strings does not affect scoping.
            elif char == "'" or char == "\"":
                # enter quote mode if not already in it
                if not in_quote:
                    # enter self.quote mode. Store the type of quote (' or ")
                    # so we know what character ends the string
                    in_quote = char            
                # check if current char is same type of quote that started the 
                # string
                elif in_quote == char:
                    # if so, leave quote mode
                    in_quote = False                
                whitespace_source += indent_if_needed(char)            
            elif in_quote:                
                # if in quoted string mode, just add chars as-is
                whitespace_source += indent_if_needed(char)

            elif char == "(":
                # we should never see brackets changing scope inside 
                # paranthesis, so track the fact that we're "in" a 
                # paranthesis-scope now. track the number of paranthesis
                # instead of using a flag, as they may be nested.
                in_paranthesis += 1
                whitespace_source += indent_if_needed(char)

            elif char == ")":
                # and track that we may be leaving a paranthesis scope.
                in_paranthesis -= 1
                whitespace_source += indent_if_needed(char)

            elif char == "[":
                # we should never see brackets changing scope inside array 
                # declarations, so track the fact that we're "in" a 
                # paranthesis-scope now. track the number of paranthesis 
                # instead of using a flag, as they may be nested.
                in_square_brackets += 1
                whitespace_source += indent_if_needed(char)
                
            elif char == "]":
                # and track that we may be leaving an array declaration.
                in_square_brackets -= 1
                whitespace_source += indent_if_needed(char)

            elif char == "=" and not (prevchar == "=" or nextchar == "="):
                # if we're about to declare something, and the next character 
                # is a bracket, it can only be a dict being declared. so track 
                # that we're entering "declaration mode".                
                in_declaration = True
                whitespace_source += indent_if_needed(char)

            elif char == "{":
                if in_dict or in_declaration or in_quote or in_paranthesis or \
                        in_square_brackets:
                    # if we're in declaration mode, inside a quote, inside 
                    # paranthesis or array declarations, a bracket can only be 
                    # the start of dict.
                    in_dict += 1                    
                    whitespace_source += indent_if_needed(char)
                else:
                    # otherwise, it must be the start of a new indentation
                    # add whitespace-indentation, instead of the actual bracket
                    level += 1
                    whitespace_source += indent_if_needed(":\n")  
                    last_was_newline = True                  

            # this may be the end of a dict, or an indentation char
            elif char == "}":
                if in_dict or in_quote or in_paranthesis or in_square_brackets:
                    # we're inside a dict, quoted string, paranthesis or array 
                    # declaration, so the curly brace can only be the end 
                    # of a dict declaration.
                    in_dict -= 1
                    whitespace_source += indent_if_needed(char)
                else:
                    # otherwise, it must be the end of an indentated block
                    # add whitespace-indentation, instead of the actual bracket
                    level -= 1       
                    whitespace_source += indent_if_needed("\n")
                    last_was_newline = True
                             
            elif char == ";":
                # beautify the source a bit by using newlines instead of
                # all the semicolons we've received on the input                
                whitespace_source += indent_if_needed("\n")
                last_was_newline = True
            else:
                # this is just any odd character as part of the python code, so
                # just add it                
                whitespace_source += indent_if_needed(char)

            # no matter what we just decided, do check if we're leaving
            # declartion mode
            if char != "=" and char != ' ' and in_declaration:
                in_declaration = False

        
        return whitespace_source

if __name__ == "__main__":



    pype = __pypecls__()
    (__opts__, args) = pype.parse_args()

    # parse user code
    if __opts__.before:
        before_code = pype.parse_source(__opts__.before)
    if __opts__.after:
        after_code = pype.parse_source(__opts__.after)

    indented_code = pype.parse_source(' '.join(args))
    
    # create pype cls
    __pypefn__  = "def pype(stdin):\n\n"        

    if __opts__.before:
        __pypefn__ += pype.indent("# 'before' code",1) + "\n"
        if __opts__.debug:
            __pypefn__ += pype.indent("print '--before'",1) + "\n"
        __pypefn__ += pype.indent(before_code,1) + "\n\n"

    if __opts__.debug:
        __pypefn__ += pype.indent("__lineno__ = 1",1) + "\n\n"        

    __pypefn__ += pype.indent("for _ in stdin:",1) + "\n"    
    if __opts__.stripnewlines:
        __pypefn__ += pype.indent( "_ = _.rstrip('\\n')",2) + "\n"
    if __opts__.debug:
        __pypefn__ += pype.indent(
            "print '== input line {0}'.format(__lineno__)",2) + "\n"
        __pypefn__ += pype.indent(
            "print '{0}'.format(_)" + "\n",2) + "\n"        
        __pypefn__ += pype.indent(
            "print '== output line {0}'.format(__lineno__)",2) + "\n"
        __pypefn__ += pype.indent(
            "__lineno__ += 1" + "\n",2) + "\n"        
    __pypefn__ += pype.indent("# 'pipe' code",2) + "\n"
    __pypefn__ += pype.indent(indented_code,2) + "\n"

    if __opts__.after:
        __pypefn__ += pype.indent("# 'after' code",1) + "\n"
        if __opts__.debug:
            __pypefn__ += pype.indent("print '--after'",1) + "\n"
        __pypefn__ += pype.indent(after_code,1) + "\n\n"

    __pypefn__ = __pypefn__.strip() + "\n"
    
    # do a bit of housekeeping to keep as much as possible out of user's 
    # namespace
    del pype,args

    # always print source to stdout if debug flag is enabled
    if __opts__.debug:
        print "Source:"
        __lineno__ = 0
        for line in __pypefn__.split("\n"):
            __lineno__ += 1            
            print " {0}: {1}".format(str(__lineno__).rjust(3), line)
        print ""
        print "Execution:"

    try:
        # and finally, create the user method
        exec(__pypefn__)        
        # and run the code
        pype(sys.stdin)    
    except:
        # to help the user in case of syntax errors, print the source
        # code will already have been output if debug == 1
        if not __opts__.debug:
            err("Source:")
            __lineno__ = 0
            for line in __pypefn__.split("\n"):
                __lineno__ += 1            
                err(" {0}: {1}".format(str(__lineno__).rjust(3), line))
            err("")
        
        # and don't forget to throw the original exception!
        raise
