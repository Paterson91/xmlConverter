import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

def dna_to_rna(dna_sequence):
    """Convert a DNA sequence to an RNA sequence by replacing T with U."""
    return dna_sequence.replace('T', 'U').replace('t', 'u')

def create_xml_output(sequences, filename='5113P_GB.xml'):
    # Create the root element
    st26 = ET.Element("ST26SequenceListing", 
                      {
                          "originalFreeTextLanguageCode": "en",
                          "dtdVersion": "V1_3",
                          "fileName": filename,
                          "softwareName": "WIPO Sequence",
                          "softwareVersion": "2.3.0",
                          "productionDate": datetime.today().strftime('%Y-%m-%d')
                      })
    
    # Add ApplicationIdentification element
    app_id = ET.SubElement(st26, "ApplicationIdentification")
    ET.SubElement(app_id, "IPOfficeCode").text = "GB"
    ET.SubElement(app_id, "ApplicationNumberText")
    ET.SubElement(app_id, "FilingDate")
    
    # Add ApplicantFileReference element
    ET.SubElement(st26, "ApplicantFileReference").text = "5113P/GB"
    
    # Add EarliestPriorityApplicationIdentification element
    priority_app_id = ET.SubElement(st26, "EarliestPriorityApplicationIdentification")
    ET.SubElement(priority_app_id, "IPOfficeCode").text = "GB"
    ET.SubElement(priority_app_id, "ApplicationNumberText").text = "2306589.9"
    ET.SubElement(priority_app_id, "FilingDate").text = "2023-05-04"
    
    # Add ApplicantName element
    ET.SubElement(st26, "ApplicantName", {"languageCode": "en"}).text = "ARGONAUTE RNA LIMITED"
    
    # Add InventionTitle element
    ET.SubElement(st26, "InventionTitle", {"languageCode": "en"}).text = "DUAL SILENCING"
    
    # Add SequenceTotalQuantity element
    ET.SubElement(st26, "SequenceTotalQuantity").text = str(len(sequences))
    
    # Add sequence data
    for seq_id, seq_info in enumerate(sequences, start=1):
        seq_data = ET.SubElement(st26, "SequenceData", {"sequenceIDNumber": str(seq_id)})
        insdseq = ET.SubElement(seq_data, "INSDSeq")
        
        # Convert DNA to RNA before adding it to the XML
        rna_sequence = dna_to_rna(seq_info['sequence'])
        
        ET.SubElement(insdseq, "INSDSeq_length").text = str(len(rna_sequence))
        ET.SubElement(insdseq, "INSDSeq_moltype").text = "RNA"
        ET.SubElement(insdseq, "INSDSeq_division").text = "PAT"
        
        # Add INSDSeq_feature-table
        feature_table = ET.SubElement(insdseq, "INSDSeq_feature-table")
        feature = ET.SubElement(feature_table, "INSDFeature")
        ET.SubElement(feature, "INSDFeature_key").text = "source"
        ET.SubElement(feature, "INSDFeature_location").text = f"1..{len(rna_sequence)}"
        
        # Add INSDFeature_quals
        quals = ET.SubElement(feature, "INSDFeature_quals")
        qual1 = ET.SubElement(quals, "INSDQualifier")
        ET.SubElement(qual1, "INSDQualifier_name").text = "mol_type"
        ET.SubElement(qual1, "INSDQualifier_value").text = "other RNA"
        
        qual2 = ET.SubElement(quals, "INSDQualifier", {"id": "q2"})
        ET.SubElement(qual2, "INSDQualifier_name").text = "organism"
        ET.SubElement(qual2, "INSDQualifier_value").text = "synthetic construct"
        
        # Add the RNA sequence itself
        ET.SubElement(insdseq, "INSDSeq_sequence").text = rna_sequence
    
    # Convert the XML tree to a pretty-printed string using minidom
    rough_string = ET.tostring(st26, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    # Write the XML with the DOCTYPE declaration to the file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<!DOCTYPE ST26SequenceListing PUBLIC "-//WIPO//DTD Sequence Listing 1.3//EN" "ST26SequenceListing_V1_3.dtd">\n')
        f.write(pretty_xml.split('\n', 1)[1])  # Skip the redundant XML declaration from toprettyxml

# Example usage
sequences = [
    {"sequence": "acgcgccgttttcgcttcg"}, 
    {"sequence": "acgcgcgattcggctttcg"},  # Example DNA sequence 1
    # Add more sequences as needed...
]

create_xml_output(sequences)
