""" Helper module for kbuildparse."""

# Copyright (C) 2014-2018 Andreas Ziegler <andreas.ziegler@fau.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Parts taken from the 'undertaker' project (https://undertaker.cs.fau.de)
# with the following authors
# Copyright (C) 2011-2012 Christian Dietrich <christian.dietrich@informatik.uni-erlangen.de>
# Copyright (C) 2011-2012 Reinhard Tartler <tartler@informatik.uni-erlangen.de>
# Copyright (C) 2012 Manuel Zerpies <manuel.f.zerpies@ww.stud.uni-erlangen.de>
# Copyright (C) 2014 Valentin Rothberg <valentinrothberg@gmail.com>
# Copyright (C) 2012-2015 Stefan Hengelein <stefan.hengelein@fau.de>

import logging
import os
import re

import kbuildparse.data_structures as DataStructures

def build_precondition(input_list, additional=None):
    """ Build a DataStructures.Precondition object from a given @input_list.
    Additional constraints from @additional are added to the Precondition."""
    alternatives = []
    for alternative in input_list:
        string = " && ".join(alternative)
        if string != "":
            alternatives.append(string)
        else:
            # This case means that at least one unconditional path was found ->
            # return no condition.
            alternatives = []
            break

    alt_string = " || ".join(alternatives)

    ret = DataStructures.Precondition()
    if additional:
        for x in additional:
            ret.add_condition(x, no_duplicates=True)

    if len(alternatives) > 1:
        ret.add_condition("(" + alt_string + ")", no_duplicates=True)
    elif len(alt_string) > 1:
        ret.add_condition(alt_string, no_duplicates=True)

    return ret


def setup_logging(log_level):
    """ setup the logging module with the given log_level """

    l = logging.WARNING # default
    if log_level == 1:
        l = logging.INFO
    elif log_level >= 2:
        l = logging.DEBUG

    logging.basicConfig(level=l)


def guess_source_for_target(target):
    """
    for the given target, try to determine its source file.
    generic version for linux and busybox

    return None if no source file could be found
    """
    for suffix in ('.c', '.S', '.s', '.l', '.y', '.ppm'):
        sourcefile = target[:-2] + suffix
        if os.path.exists(sourcefile):
            return sourcefile
    return None


def remove_makefile_comment(line):
    """ Strips everything after the first # (Makefile comment) from a line."""
    return line.split("#", 1)[0].rstrip()


def get_multiline_from_file(infile):
    """ Reads a line from infile. If the line ends with a line continuation,
    it is substituted with a space and the next line is appended. Returns
    (True, line) if reading has succeeded, (False, "") otherwise. The boolean
    value is required to distinguish an error from empty lines in the input
    (which might also occur by stripping the comment from a line which only
    contains that comment)."""
    line = ""
    current = infile.readline()
    if not current:
        return (False, "")
    current = remove_makefile_comment(current)
    while current.endswith('\\'):
        current = current.replace('\\', ' ')
        line += current
        current = infile.readline()
        if not current:
            break
        current = remove_makefile_comment(current)
    line += current
    line.rstrip()
    return (True, line)


def get_config_string(item, model=None):
    """ Return a string with CONFIG_ for a given item. If the item is
    a tristate symbol in model, CONFIG_$(item)_MODULE is added as an
    alternative."""
    if item.startswith("CONFIG_"):
        item = item[7:]
    if model and model.get_type(item) == "tristate":
        return "(CONFIG_" + item + " || CONFIG_" + item + "_MODULE)"
    return "CONFIG_" + item
