#!/usr/bin/env python

################################################################################
# GMTcsh2dos.py
# -------------------------------------------------
#  Version: 0.1
#  Author:  Simon Dreutter
#  License: GNU Generic Public License v3.0 / 2015
# -------------------------------------------------
################################################################################
#
#  This is a script for translating simple GMT (Generic Mapping Tools) Unix
#  csh scripts into DOS batch files. It will do some simple changes in the
#  Syntax (comments, etc.) to ensure the compatibility. It is not meant for
#  translating unix2dos in general, since this is not possible!
#
#  Run script like so:
#     GMTcsh2dos.py <Inputfile>
#
################################################################################

# import modules
import sys

#=================================================
#              open GMT csh script:
#=================================================

try:
    filename = sys.argv[1]
    print('\nInput file:   ' + filename)
except IndexError:
    print('\nNo Input file specified. Canelled!\n')
    sys.exit()

f = open(filename,'rb')
csh = f.read()
f.close()


#=================================================
#      start with some simple replacement:
#=================================================

# ('\n','')       for multiline commands
# ('\t','')       for tabs inbetween command lines
# ('>!','>')      for first time calling of the PS_FILE
# ('= ','=')      to avoid spaces in the variable settings
# ('=>','= >')    to recover '= >' in the -T option of grd2cpt
# ('rm -f','del') unix2dos syntax for deleting files
lines = csh.replace('\\\n','').replace('>!','>').replace('= ','=').replace('=>','= >').replace('rm -f','del').split('\n')


#=================================================
# go on with some more complicated replacements:
#=================================================

# counter
i = 0

# list of script variables
var = []

# loop through all lines and do stuff
for line in lines:
    # delete \t in lines that are not comments
    if not line.startswith('#'):
        lines[i] = line.replace('\t','')
        line = lines[i]
    # check for lines that contain a command and a following comment and
    # get rid of the comment
    if '#' in line and not line.startswith('#'):
        lines[i] = line.split('#')[0]
        line = lines[i]
    # replace comment symbols ('#','REM ')
    if line.startswith('#'):
        lines[i] = line.replace('#','REM ',1)
        line = lines[i]
    
    # look for variable settings and append the to var list
    if line.startswith('set'):
        var.append(line.split('=')[0].split(' ')[1])
    # loop through all variables in each line to change '$VAR' to '%VAR%'
    for v in var:
        v = '$'+v
        if v in line:
            lines[i] = line.replace(v,'%'+v[1:]+'%')
            line = lines[i]
    
    # DOS  does not accept variables within " ", therefore get rid of them
    if '"%' in line:
        lines[i] = line.replace('"%','%')
        line = lines[i]
    if '%"' in line:
        lines[i] = line.replace('%"','%')
        line = lines[i]
    
    # count up
    i = i + 1


#=================================================
#                write .bat file:
#=================================================

# file handling
filename = filename.split('.')[0] + '.bat'
f = open(filename,'wb')

# 'echo off' to make echos visible in DOS cmd
f.write('@echo off\r\n')
# write lines but skip initial '#! /bin/csh' line and 'Preview' command line
for line in lines:
    if '! /bin' in line:
        continue
    if 'Preview' in line:
        continue
    f.write(line + '\r\n')
# 'echo on'
f.write('@echo on\r\n')
# close file
f.close()


#=================================================
#                  all done:
#=================================================
print('Output file:  ' + filename)
print('\nAll Done!\n')
