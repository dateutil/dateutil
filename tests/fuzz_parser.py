#!/usr/bin/python3

from decimal import InvalidOperation
import atheris
import sys


with atheris.instrument_imports():
    from dateutil.parser import parse, ParserError


def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    try:
        parse(fdp.ConsumeString(len(data)))
    except (ParserError, OverflowError, InvalidOperation):
        pass


atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
