import sys
import ast
import os
from configparser import ConfigParser, ExtendedInterpolation

if len(sys.argv) == 1:
    print("Usage: " + sys.argv[0] + " [host.cfg] [out.htaccess]")
    sys.exit()

filename = ".htaccess"
if len(sys.argv) > 2:
    filename = sys.argv[2]

parser = ConfigParser(interpolation=ExtendedInterpolation())
print("Generating www/" + filename + " from template.cfg")
parser.read('template.cfg')

if len(sys.argv) > 1:
    if os.path.isfile(sys.argv[1] + ".cfg"):
        print("Applying config values from: " + sys.argv[1] + ".cfg to www/" + filename)
        parser.read(sys.argv[1] + ".cfg")
    else:
        print("Couldn't find " + sys.argv[1] + ".cfg" + " config file")


def use_bots_selected(section):
    if parser.has_option(section, "use_bots"):
        use_bot = parser.get(section, "use_bots")
        return use_bot == "True" or use_bot == "true"
    return False

def writeline(string):
    out.write(string + "\n")

def header():
    writeline("# PLEASE DO NOT MODIFY THIS IS A GENERATED FILE!!!!")
    writeline("RewriteEngine On")
    writeline("")
    http_forward = parser.get("options", "http_forward")
    if http_forward == "true" or http_forward == "True":
        writeline("RewriteCond %{HTTPS}  !=on")
        writeline("RewriteRule ^/?(.*) https://%{SERVER_NAME}/$1 [R,L]")
        writeline("")
    if parser.has_option("options", "show_errordoc"):
        error_doc()

def error_doc():
    redirect = parser.get("options", "show_errordoc")
    if redirect == "true" or redirect == "True":
        mgihome_url = parser.get("urls", "mgihome_url")
        writeline("# --- Default Error Document Location")
        writeline("ErrorDocument 404 " + mgihome_url + "/other/Error404.shtml")
        writeline("")

def generate_bots(use_bots, url, match, path):
    if use_bots and parser.has_option("options", "bots"):
        writeline("")
        bots = parser.get("options", "bots").split(",")
        for bot in bots[:-1]:
            writeline("RewriteCond %{HTTP_USER_AGENT} \"" + bot + "\"\t\t\t[NC,OR]")
        writeline("RewriteCond %{HTTP_USER_AGENT} \"" + bots[-1] + "\"\t\t\t[NC]")

        writeline("RewriteRule ^" + match + "(.*)\t\t" + url + "/" + path + "/$1 [P,L]")
        writeline("RewriteCond %{HTTP_REFERER} =\"-\"")
        writeline("RewriteCond %{HTTP_USER_AGENT} =\"-\"")
        writeline("RewriteRule ^" + match + "(.*)\t\t" + url + "/" + path + "/$1 [P,L]")

def mgi_homeurls():
    if parser.has_option("mgi_home_urls", "paths"):
        writeline("# --- Default URL's for MGI Home pages")
        homepages_url = parser.get("urls", "homepages_url")
        for path in parser.get("mgi_home_urls", "paths").split(","):
            writeline("RewriteRule ^" + path + "\t\t" + homepages_url + "/" + path + " [P,L]")
        writeline("")

def menu_urls():
    if parser.has_option("menu_urls", "paths"):
        writeline("# --- Default URL's for MGI Home menu pages")
        menu_url = parser.get("urls", "menus_url")
        for path in parser.get("menu_urls", "paths").split(","):
            writeline("RewriteRule ^" + path + "\t\t" + menu_url + "/" + path + " [P,L]")
            writeline("RewriteRule ^menus/" + path + "\t\t" + menu_url + "/" + path + " [P,L]")
        writeline("")

def fewi_urls():
    if parser.has_option("fewi_urls", "paths"):
        writeline("# --- Default URL's for FEWI pages")
        fewi_url = parser.get("urls", "fewi_url")
        fewi_bot_url = parser.get("urls", "fewi_bot_url")
        for path in parser.get("fewi_urls", "paths").split(","):
            generate_bots(use_bots_selected("fewi_urls"), fewi_bot_url, path, path)
            writeline("RewriteRule ^" + path + "(.*)\t\t" + fewi_url + "/" + path + "/$1 [P,L]")
        writeline("")

def batch_urls():
    if parser.has_option("batch", "paths"):
        writeline("# --- Default URL's for FEWI batch pages")
        use_separate_batch = parser.get("batch", "use_separate_batch")
        for path in parser.get("batch", "paths").split(","):
            if use_separate_batch == "true":
                url = parser.get("urls", "fewi_batch_url")
                fewi_bot_url = parser.get("urls", "fewi_bot_url")
                generate_bots(use_bots_selected("batch"), fewi_bot_url, path, path)
                writeline("RewriteRule ^" + path + "(.*)\t\t" + url + "/" + path + "/$1 [P,L]")
            else:
                url = parser.get("urls", "fewi_url")
                writeline("RewriteRule ^" + path + "(.*)\t\t" + url + "/" + path + "/$1 [P,L]")
        writeline("")

def custom_urls():
    writeline("# --- Custom rules not defined anywhere else")
    for sec in parser.sections():
        if sec.startswith("^"):
            if parser.has_option(sec, "comment"):
                writeline("# " + parser.get(sec, "comment"))
            url = parser.get(sec, "path")
            
            if parser.has_option(sec, "conditions"):
                conditions = parser.get(sec, "conditions")
                conditions = ast.literal_eval(conditions)
                keys = list(conditions.keys())
                keys.sort()
                keys.reverse()
                for key in keys:
                   writeline("RewriteCond " + key + "\t\t" + conditions[key] + "\t\t[NC]")

            if parser.has_option(sec, "flags"):
                writeline("RewriteRule " + sec + "\t\t" + url + " " + parser.get(sec, "flags"))
            else:
                writeline("RewriteRule " + sec + "\t\t" + url + " [P,L]")
            writeline("")

def creHtaccess():
    fewi_url = parser.get("urls", "fewi_url")
    creOut.write("# PLEASE DO NOT MODIFY THIS IS A GENERATED FILE!!!!" + "\n")
    creOut.write("RewriteEngine On" + "\n")
    creOut.write("" + "\n")
    creOut.write("RewriteCond %{REQUEST_URI} !=/server-status [NC]" + "\n")
    creOut.write("RewriteRule ^(.*)$\t\t" + fewi_url + "/home/recombinase/ [P,L]" + "\n")
    creOut.write("" + "\n")

out = open("www/" + filename, 'w')
header()
mgi_homeurls()
menu_urls()
batch_urls()
fewi_urls()
custom_urls()
out.close()

creOut = open("cre/" + filename, 'w')
creHtaccess()
creOut.close()
