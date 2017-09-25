#!/usr/bin/env python
#
# Create project files for all BTstack embedded examples in local port/esp32 folder

import os
import shutil
import sys
import time
import subprocess

mk_template = '''#
# BTstack example 'EXAMPLE' for ESP32 port
#
# Generated by TOOL
# On DATE

PROJECT_NAME := EXAMPLE

include $(IDF_PATH)/make/project.mk
'''

gatt_update_template = '''#!/usr/bin/env python
#
# Update EXAMPLE.h from EXAMPLE.gatt
import os
import sys

script_path  = os.path.abspath(os.path.dirname(sys.argv[0]))
compile_gatt = os.environ['IDF_PATH'] + '/components/btstack/tool/compile_gatt.py'
print("Creating src/gatt_battery_query.h from src/gatt_battery_query.gatt")
sys.argv= [compile_gatt, script_path + "/main/EXAMPLE.gatt", script_path + "/main/EXAMPLE.h"]
exec(open(compile_gatt).read(), globals())
'''

# get script path
script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

# path to examples
examples_embedded = script_path + "/../../example/"

# path to samples
examples_folder = script_path + "/examples/"

print("Creating examples folder")
if not os.path.exists(examples_folder):
    os.makedirs(examples_folder)

print("Creating examples in examples folder")

# iterate over btstack examples
for file in os.listdir(examples_embedded):
    if not file.endswith(".c"):
        continue
    if file in ['panu_demo.c', 'sco_demo_util.c']:
        continue

    example = file[:-2]
    gatt_path = examples_embedded + example + ".gatt"

    # create folder
    apps_folder = examples_folder + example + "/"
    if os.path.exists(apps_folder):
        shutil.rmtree(apps_folder)
    os.makedirs(apps_folder)

    # copy files
    for item in ['sdkconfig', 'set_port.sh']:
        shutil.copyfile(script_path + '/template/' + item, apps_folder + '/' + item)

    # mark set_port.sh as executable
    os.chmod(apps_folder + '/set_port.sh', 0o755)

    # create Makefile file
    with open(apps_folder + "Makefile", "wt") as fout:
        fout.write(mk_template.replace("EXAMPLE", example).replace("TOOL", script_path).replace("DATE",time.strftime("%c")))

    # create main folder
    main_folder = apps_folder + "main/"
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    # copy example file
    shutil.copyfile(examples_embedded + file, apps_folder + "/main/" + example + ".c")

    # add sco_demo_util.c for audio examples
    if example in ['hfp_ag_demo','hfp_hf_demo', 'hsp_ag_demo', 'hsp_hf_demo']:
        shutil.copy(examples_embedded + 'sco_demo_util.c', apps_folder + '/main/')
        shutil.copy(examples_embedded + 'sco_demo_util.h', apps_folder + '/main/')

    # add component.mk file to main folder
    shutil.copyfile(script_path + '/template/main/component.mk', apps_folder + "/main/component.mk")

    # create update_gatt.sh if .gatt file is present
    gatt_path = examples_embedded + example + ".gatt"
    if os.path.exists(gatt_path):
        shutil.copy(gatt_path, apps_folder + "/main/" + example + ".gatt")
        update_gatt_script = apps_folder + "update_gatt_db.py"
        with open(update_gatt_script, "wt") as fout:
            fout.write(gatt_update_template.replace("EXAMPLE", example))
        os.chmod(update_gatt_script, 0o755)
        subprocess.call(update_gatt_script + "> /dev/null", shell=True)
        print("- %s including compiled GATT DB" % example)
    else:
        print("- %s" % example)
