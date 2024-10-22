from flask import Flask, render_template, request, send_from_directory
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

app = Flask(__name__)
OUTPUT_FOLDER = 'output'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def dna_to_rna(dna_sequence):
    """Convert a DNA sequence to an RNA sequence by replacing T with U."""
    return dna_sequence.replace('T', 'U').replace('t', 'u')

def create_xml_output(sequences, applicant_file_reference, applicant_name, invention_title, file_name):
    st26 = ET.Element("ST26SequenceListing", 
                      {
                          "originalFreeTextLanguageCode": "en",
                          "dtdVersion": "V1_3",
                          "fileName": file_name,
                          "softwareName": "InSilico Consulting Limited Sequence",
                          "softwareVersion": "0.0.1",
                          "productionDate": datetime.today().strftime('%Y-%m-%d')
                      })
    
    app_id = ET.SubElement(st26, "ApplicationIdentification")
    ET.SubElement(app_id, "IPOfficeCode").text = "GB"
    ET.SubElement(app_id, "ApplicationNumberText")
    ET.SubElement(app_id, "FilingDate")
    ET.SubElement(st26, "ApplicantFileReference").text = applicant_file_reference
    priority_app_id = ET.SubElement(st26, "EarliestPriorityApplicationIdentification")
    ET.SubElement(priority_app_id, "IPOfficeCode").text = "GB"
    ET.SubElement(priority_app_id, "ApplicationNumberText").text = "2306589.9"
    ET.SubElement(priority_app_id, "FilingDate").text = "2023-05-04"
    ET.SubElement(st26, "ApplicantName", {"languageCode": "en"}).text = applicant_name
    ET.SubElement(st26, "InventionTitle", {"languageCode": "en"}).text = invention_title
    ET.SubElement(st26, "SequenceTotalQuantity").text = str(len(sequences))
    
    for seq_id, dna_sequence in enumerate(sequences, start=1):
        rna_sequence = dna_to_rna(dna_sequence.strip())
        seq_data = ET.SubElement(st26, "SequenceData", {"sequenceIDNumber": str(seq_id)})
        insdseq = ET.SubElement(seq_data, "INSDSeq")
        ET.SubElement(insdseq, "INSDSeq_length").text = str(len(rna_sequence))
        ET.SubElement(insdseq, "INSDSeq_moltype").text = "RNA"
        ET.SubElement(insdseq, "INSDSeq_division").text = "PAT"
        
        feature_table = ET.SubElement(insdseq, "INSDSeq_feature-table")
        feature = ET.SubElement(feature_table, "INSDFeature")
        ET.SubElement(feature, "INSDFeature_key").text = "source"
        ET.SubElement(feature, "INSDFeature_location").text = f"1..{len(rna_sequence)}"
        quals = ET.SubElement(feature, "INSDFeature_quals")
        qual1 = ET.SubElement(quals, "INSDQualifier")
        ET.SubElement(qual1, "INSDQualifier_name").text = "mol_type"
        ET.SubElement(qual1, "INSDQualifier_value").text = "other RNA"
        qual2 = ET.SubElement(quals, "INSDQualifier", {"id": "q2"})
        ET.SubElement(qual2, "INSDQualifier_name").text = "organism"
        ET.SubElement(qual2, "INSDQualifier_value").text = "synthetic construct"
        ET.SubElement(insdseq, "INSDSeq_sequence").text = rna_sequence
    
    rough_string = ET.tostring(st26, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")
    return pretty_xml


def save_xml_to_file(xml_content, filename='5113P_GB.xml'):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<!DOCTYPE ST26SequenceListing PUBLIC "-//WIPO//DTD Sequence Listing 1.3//EN" "ST26SequenceListing_V1_3.dtd">\n')
        f.write(xml_content.split('\n', 1)[1])  # Skip the redundant XML declaration from toprettyxml
    return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sequences = request.form['sequences'].strip().splitlines()
        applicant_file_reference = request.form['applicantFileReference'].strip()
        applicant_name = request.form['applicantName'].strip()
        invention_title = request.form['inventionTitle'].strip()
        download_file_name = request.form['downloadFileName'].strip()

        if sequences:
            xml_content = create_xml_output(sequences, applicant_file_reference, applicant_name, invention_title, download_file_name)
            output_filename = save_xml_to_file(xml_content, download_file_name)
            return render_template('index.html', xml_content=xml_content, filename=output_filename)
    return render_template('index.html', xml_content=None)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found.", 404

if __name__ == '__main__':
    app.run(debug=True)
