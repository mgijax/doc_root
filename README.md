# Generate .htaccess (using Python ConfigParser)

### Product Setup

```bash
./Install
```

### Config Syntax
doc_root uses Python's ConfigParser to load and parse .cfg files, into a python dictionary object. The basic format of the file is:

```
[section1]
name1 = value3
name2 = value4
```

Advanced config example.

```
[config]
host = www.informatics.jax.org
host_url = http://${host}
url = ${host_url}/path/to/file

[section2]
url2 = ${config:host_url}/another/path/to/file
```

Another nice feature of the ConfigParser is that multiple configs can be loaded and override existing variables:

```
config.cfg:
[config]
host = www.informatics.jax.org
host_url = http://${host}
url = ${host_url}/path/to/file

[section2]
url2 = ${config:host_url}/another/path/to/file


host1.cfg:
[config]
host = redbob.informatics.jax.org
```

If config.cfg is loaded first then host1.cfg is loaded all the URL's will be changed based on the new value of "host" in the config file.

### Template

The main file for generating htaccess is template.cfg. After that other host files can be applied to change all the values located in the files. Once the new values have been applied the script moves on to generate the .htaccess file.

### Usage

gen_htaccess takes two paramaters.

- Template file (Required): This is the file that will be applied to the main template.cfg file.
- Output file (Optional): If this option is specified then the output of the script will be placed into a file with this name overriding any existing file by the same name. If this option is not present, then the output will be placed into a file called .htaccess.

```
>python gen_htaccess.py pub1
Generating .htaccess from template.cfg
Applying config values from: pub1.cfg to .htaccess
>

>python gen_htaccess.py pub1 output.htaccess
Generating output.htaccess from template.cfg
Applying config values from: pub1.cfg to output.htaccess
>
```
