from configparser import ConfigParser, ExtendedInterpolation

parser = ConfigParser(interpolation=ExtendedInterpolation())

parser.read('template.cfg')



for sec in parser.sections():
    for option in parser[sec]:
        print option
        print parser[sec][option]

