import os
import re

def get_export_file_from_ontorefine(data_file, mapping_file, export_file, ontorefine_cmd, ontorefine_url, project_name):
    project_id = create_ontorefine_project(data_file, ontorefine_cmd, ontorefine_url, project_name)
    create_ttl_file_from_mapping(project_id, mapping_file, export_file, ontorefine_cmd, ontorefine_url)
    remove_ontorefine_project(project_id, ontorefine_cmd, ontorefine_url)

def create_ontorefine_project(data_file, ontorefine_cmd, ontorefine_url, project_name):
    # Launch Ontorefine before launching this command
    cmd = f"{ontorefine_cmd} create \"{data_file}\" -u \"{ontorefine_url}\" -n \"{project_name}\""
    msg = os.popen(cmd)
    msg_content = msg.read()

    # Get project_id from message given by CLI
    try:
        project_id = re.findall("identifier: ([0-9]{1,})", msg_content)[0]
    except IndexError:
        project_id = None

    return project_id

def create_ttl_file_from_mapping(project_id, mapping_file, export_file, ontorefine_cmd, ontorefine_url):
    cmd = f"{ontorefine_cmd} rdf \"{project_id}\" -u {ontorefine_url} -m \"{mapping_file}\""
    out_content = os.popen(cmd)
    out_file = open(export_file, "w")
    out_file.write(out_content.read())
    out_file.close()

def remove_ontorefine_project(project_id, ontorefine_cmd, ontorefine_url):
    cmd = f"{ontorefine_cmd} delete \"{project_id}\" -u {ontorefine_url}"
    os.system(cmd)