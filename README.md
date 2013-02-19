
PyProfGen
=========

PyProfGen generates HTML documentation of the result of `gprof(1)`.

Sample Output
-------------

See the output here.

Installation
------------

    $ git clone https://github.com/cinsk/pyprofgen.git
    $ cd pyprofgen
    $ make all
    $ make install
    
Usage
-----

    $ ls
    demo.c
    $ gcc -g -pg -o demo demo.c -lc_p
    $ ./demo
    $ ls -F
    demo*   demo.c   gmon.out
    $ pyprofgen --help
    USAGE: pyprofgen [OPTION...] executable [gmon.out]
    Generate HTML documents from gmon.out

      -d DIR,               Set the output directory to DIR,
          --directory=DIR     (default: doc)
      -q, --quiet           Quite mode, (default: verbose mode)
      -h, --help            Show help message
      -v, --version         Print version information

    Report bugs to <cinsk at cinsk.org>.

    $ pyprofgen demo gmon.out
    ...
    $ ls -F
    demo*   demo.c   gmon.out   prof/
    $ elinks prof/html/index.html	# use your favorite browsers.
    $ _
    

Requirements
------------

As the package name implies, PyProfGen uses Python to interpret the
output of `gprof(1)`.  I tested on two environments:

- Redhat Fedora Core 2:
- Python version 2.3.3
- graphviz version 1.12
- gprof(1) in binutils version 2.15.90

- Gentoo Linux 2005.0
- Python version 2.3.5
- graphviz version 2.2.1
- gprof(1) in binutils version 2.15.92

