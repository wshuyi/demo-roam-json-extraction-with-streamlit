import streamlit as st
from pathlib import Path
from zipfile import ZipFile
import shutil
import json
from io import StringIO
import base64
import os

def extract_json_from_zip(json_zip):
    extracted_dir = Path("./extracted")

    if extracted_dir.exists():
        shutil.rmtree(extracted_dir)
    extracted_dir.mkdir()

    with ZipFile(json_zip, 'r') as zipObj:
        zipObj.extractall(extracted_dir)

    exported_json = list(Path(extracted_dir).glob("*.json"))[0]
    shutil.rmtree(extracted_dir)
    return exported_json







def decide_page_export(item, tags_black_list, tags_white_list):
    
    def export_decide_with_two_list(mystr, tags_black_list, tags_white_list):
        for tag in tags_black_list:
            # if in black list
            if mystr.find(f'#[[{tag}]]')>=0 or mystr.find(f'#{tag}')>=0:
                return False
        for tag in tags_white_list:
            # if in white list
            if mystr.find(f'#[[{tag}]]')>=0 or mystr.find(f'#{tag}')>=0:
                return True
        return None

    flag_export_item = False

    try:
        for child in item['children']:
            if child['string'].find('#[[')>=0:
                #contains tag
                decision = export_decide_with_two_list(child['string'], tags_black_list, tags_white_list)
                if decision == False:
                    #contains black tag
                    flag_export_item = False
                    break
                elif decision == True:
                    #should export for now
                    flag_export_item = True
    except:
        pass
    return flag_export_item


st.title("Extraction of Roam JSON file")

file_type = st.radio("Your file type:", ("json", "zip"))

uploaded_file = st.file_uploader("Upload your JSON or zipped file", type=["json", "zip"])



if uploaded_file is not None:

    if file_type == "json":
        stringio = StringIO(uploaded_file.read().decode("utf-8"))
        json_content = json.loads(stringio.read())
    else: # zip file
        extracted_json_file = extract_json_from_zip(uploaded_file)
        with open(extracted_json_file) as f:
            json_content = json.load(f)
    st.write(f"{len(json_content)} items in your JSON file")
    tags_white_list = st.text_area("Tags in the white list:", 'roamconfig\nevergreen').split('\n')
    tags_black_list = st.text_area("Tags in the black list", 'private\nzsxq\nmonetize').split('\n')
    if st.button("extract!"):
        lst_export_objects = []
        for item in json_content:
            flag_export_item = decide_page_export(item, tags_black_list, tags_white_list)
            if flag_export_item:
                lst_export_objects.append(item)

        st.write(f"{len(lst_export_objects)} objects extracted!")

        out_json = Path("extracted.json")        
        with open(out_json, "w") as f:
            json.dump(lst_export_objects, f, ensure_ascii=False)

        out_json_zip = Path("output.zip")
        with ZipFile(out_json_zip, "w") as zip:
            zip.write(out_json)

        with open(out_json_zip, "rb") as f:
            bytes = f.read()
            b64 = base64.b64encode(bytes).decode()
            href = f'<a href="data:file/zip;base64,{b64}" download=\'{out_json_zip}\'>\
                Click to download\
            </a>'

        st.markdown(href, unsafe_allow_html=True)

        # clean up
        os.remove(out_json)
        os.remove(out_json_zip)

    
