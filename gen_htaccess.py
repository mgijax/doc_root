#!virtenv/bin/python

import sys
import ast
import os
from configparser import ConfigParser, ExtendedInterpolation

if len(sys.argv) == 1:
    print "Usage: " + sys.argv[0] + " [host.cfg] [out.htaccess]"
    sys.exit()

filename = ".htaccess"
if len(sys.argv) > 2:
    filename = sys.argv[2]

parser = ConfigParser(interpolation=ExtendedInterpolation())
print "Generating www/" + filename + " from template.cfg"
parser.read('template.cfg')

if len(sys.argv) > 1:
    if os.path.isfile(sys.argv[1] + ".cfg"):
        print "Applying config values from: " + sys.argv[1] + ".cfg to www/" + filename
        parser.read(sys.argv[1] + ".cfg")
    else:
        print "Couldn't find " + sys.argv[1] + ".cfg" + " config file"


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
    if parser.has_option("options", "blocked_ips"):
        blocked_ips()
    if parser.has_option("options", "show_redirect"):
        default_public_redirect()
    if parser.has_option("options", "show_errordoc"):
        error_doc()

def blocked_ips():
    blocked_ip_list = parser.get("options", "blocked_ips")
    if len(blocked_ip_list) > 0:
        ips = blocked_ip_list.split(',')
        writeline("# --- BLOCKED USERS & BOTS")
        writeline("order allow,deny")
        for ip in ips:
            writeline("deny from " + ip)
        writeline("allow from all")
        writeline("")

def default_public_redirect():
    redirect = parser.get("options", "show_redirect")
    if redirect == "true" or redirect == "True":
        www_host = parser.get("hosts", "www_host")
        writeline("# --- REDIRECT Non host urls to Host urls")
        writeline("RewriteCond %{HTTP_HOST} !^" + www_host + "$ [NC]")
        writeline("RewriteRule ^(.*)$ http://" + www_host + "/$1 [R=301,L]")
        writeline("")

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
        for bot in bots:
            writeline("RewriteCond %{HTTP_USER_AGENT} \"" + bot + "\"\t\t\t[NC,OR]")

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

def searchtool_urls():
    path = parser.get("searchtool", "path")
    url = parser.get("urls", "search_tool_url")
    search_tool_bot_url = parser.get("urls", "search_tool_bot_url")
    generate_bots(use_bots_selected("searchtool"), search_tool_bot_url, "searchtool", path)
    writeline("RewriteRule ^searchtool(.*)\t\t" + url + "/" + path + "/$1 [P,L]")

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
		keys = conditions.keys()
		keys.sort()
		keys.reverse()
		for key in keys:
                   writeline("RewriteCond " + key + "\t\t" + conditions[key] + "\t\t[NC]")

            if parser.has_option(sec, "flags"):
                writeline("RewriteRule " + sec + "\t\t" + url + " " + parser.get(sec, "flags"))
            else:
                writeline("RewriteRule " + sec + "\t\t" + url + " [P,L]")
            writeline("")

out = open("www/" + filename, 'w')
header()
mgi_homeurls()
menu_urls()
fewi_urls()
searchtool_urls()
custom_urls()
out.close()
