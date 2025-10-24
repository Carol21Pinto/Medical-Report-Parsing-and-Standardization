import re
from datetime import datetime

def extract_patient_info(text):
    """Extract patient demographics - enhanced for multiple formats"""
    patient_data = {
        "patient_name": None,
        "age": None,
        "sex": None,
        "uhid": None,
        "episode": None,
        "ref_doctor": None,
        "mobile_no": None,
        "ward": None,
        "bed": None
    }
    
    # Patient Name - multiple patterns
    name_patterns = [
        r'PATIENT\s+NAME\s*[:=]?\s*([A-Z\s]+?)(?:\s+Age|UHID|IPID|Referred|$)',
        r'Patient\s+Name\s*[:=]\s*([A-Za-z\s\.]+?)(?:\s+Age|UHID|$)',
        r'Patient\s*[:=]?\s*([A-Za-z\s\.]+?)(?:\s+SIREESHA|$)',
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            patient_data["patient_name"] = match.group(1).strip()
            break
    
    # Age and Sex - multiple formats
    age_sex_patterns = [
        r'Age[/\\]Sex\s*[:=]?\s*(\d+)\s*Year.*?\(?(Male|Female)\)?',
        r'Age\s*[:=]?\s*(\d+).*?([MaleFemale]+)',
        r'(\d{2,3})\s*[Yy](?:ear)?.*?([MaleFemale]+)',
    ]
    for pattern in age_sex_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                patient_data["age"] = int(match.group(1))
                patient_data["sex"] = match.group(2)[:1].upper()  # M or F
                break
            except:
                continue
    
    # UHID / Patient ID / Admission No
    uhid_patterns = [
        r'(?:UHID|IPID|Patient\s*ID|MRN|Admn\s*No)\s*[:=]\s*([A-Z0-9\.\-]+)',
    ]
    for pattern in uhid_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            patient_data["uhid"] = match.group(1).strip()
            break
    
    # Episode
    episode_match = re.search(r'Episode\s*[:=]\s*([A-Z0-9\-]+)', text, re.IGNORECASE)
    if episode_match:
        patient_data["episode"] = episode_match.group(1).strip()
    
    # Referring Doctor / Consultant
    doctor_patterns = [
        r'(?:Referred\s+By|Ref\.?\s*Doctor|By)\s*[:=]\s*([A-Za-z\s\.\/]+?)(?:\s+Ward|Date|Report|$)',
    ]
    for pattern in doctor_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doctor_name = match.group(1).strip()
            # Clean up common false matches
            if len(doctor_name) > 3 and 'HOSPITAL' not in doctor_name.upper():
                patient_data["ref_doctor"] = doctor_name
                break
    
    # Hospital/Facility
    facility_patterns = [
        r'(?:UDHRAN|Hospital)\s+HOSPITAL',
        r'PARIDHI\s+PATHOLOGY',
        r'DEPARTMENT\s+OF\s+PATHOLOGY',
    ]
    for pattern in facility_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            patient_data["facility"] = match.group(0).strip()
            break
    
    return patient_data


def extract_order_info(text):
    """Extract order and report metadata"""
    order_data = {
        "order_date": None,
        "bill_no": None,
        "bill_date": None,
        "facility": None,
        "sample_no": None,
        "service_no": None,
        "collection_date": None,
        "report_date": None,
    }
    
    # Date patterns
    date_pattern = r'(\d{1,2}[-/]\w{3}[-/]\d{2,4}(?:\s+\d{1,2}:\d{2}(?:\s*[ap]m)?)?)'
    
    # Bill Date
    bill_date_match = re.search(rf'Bill\s+Date\s*[:=]?\s*{date_pattern}', text, re.IGNORECASE)
    if bill_date_match:
        order_data["bill_date"] = bill_date_match.group(1)
    
    # Report Date
    report_date_match = re.search(rf'(?:Report|REP)\s*\.?\s*(?:Date|DATE)\s*[:=]?\s*{date_pattern}', text, re.IGNORECASE)
    if report_date_match:
        order_data["report_date"] = report_date_match.group(1)
    
    # Collection Date
    collection_match = re.search(rf'(?:Collec\.?|Collection)\s*Date\s*[:=]?\s*{date_pattern}', text, re.IGNORECASE)
    if collection_match:
        order_data["collection_date"] = collection_match.group(1)
    
    # Service Number
    service_match = re.search(r'Service\s*No\s*[:=]?\s*([A-Z0-9]+)', text, re.IGNORECASE)
    if service_match:
        order_data["service_no"] = service_match.group(1)
    
    # Bill Number - not present in these reports
    
    # Facility
    facility_patterns = [
        r'(UDHRAN\s+HOSPITAL)',
        r'(PARIDHI\s+PATHOLOGY)',
        r'(DEPARTMENT\s+OF\s+PATHOLOGY)',
    ]
    for pattern in facility_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            order_data["facility"] = match.group(1)
            break
    
    return order_data


def extract_lab_tests_universal(text):
    """
    Universal lab test extraction - handles ALL report formats
    """
    lab_results = []
    
    # Split into lines
    lines = text.split('\n')
    
    # Track if in lab section
    in_lab_section = False
    current_section = None
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Detect section headers
        if any(header in line_stripped.upper() for header in ['BIOCHEMISTRY', 'LFT', 'LIVER FUNCTION TEST', 'DIFFERENTIAL COUNT', 'INVESTIGATIONS']):
            in_lab_section = True
            current_section = line_stripped
            continue
        
        # Skip empty lines and pure headers
        if len(line_stripped) < 3:
            continue
        if line_stripped.upper() in ['VALUE', 'UNIT', 'REF.RANGE', 'REFERENCE', 'RESULT', 'SPECIMEN', 'METHOD']:
            continue
        
        # Pattern 1: Test name at start, value and unit in middle, reference at end
        # Example: "TOTAL BILIRUBIN 1.8 mg/dl 0.4-1.0"
        pattern1 = r'^([A-Z][A-Za-z\s/\(\)\-\.,]+?)\s+([\d\.]+)\s*([↑↓\*]?[HL]?)?\s*([A-Za-z/%\^:]+(?:/[A-Za-z0-9\^]+)?)\s*([\d\.\-<>\s:]+)?$'
        match1 = re.match(pattern1, line_stripped)
        
        if match1:
            test_name = match1.group(1).strip()
            value = match1.group(2)
            abnormal_flag = match1.group(3) if match1.group(3) else ""
            unit = match1.group(4) if match1.group(4) else "-"
            ref_range = match1.group(5).strip() if match1.group(5) else "N/A"
            
            # Clean test name
            test_name = clean_test_name(test_name)
            
            # Determine status
            status = determine_status_from_markers(line, abnormal_flag)
            
            if len(test_name) >= 3 and test_name.upper() not in ['METHOD', 'NOTE', 'REMARKS', 'SAMPLE TYPE']:
                lab_results.append({
                    "test_name": test_name,
                    "value": value,
                    "unit": unit,
                    "reference_range": ref_range,
                    "status": status
                })
                continue
        
        # Pattern 2: For differential count style (test name followed by number and %)
        # Example: "Neutrophils. 58 20 - 45 %"
        pattern2 = r'^([A-Za-z\s\.]+?)\s+([\d\.]+)\s+([↑↓]?)\s*([\d\.\-\s]+)\s*(%|IU/L|mg/dl|gm/dl|g/L|RATIO)?'
        match2 = re.search(pattern2, line_stripped)
        
        if match2 and not match1:
            test_name = match2.group(1).strip()
            value = match2.group(2)
            abnormal_flag = match2.group(3) if match2.group(3) else ""
            ref_range = match2.group(4).strip() if match2.group(4) else "N/A"
            unit = match2.group(5) if match2.group(5) else "%"
            
            test_name = clean_test_name(test_name)
            status = determine_status_from_markers(line, abnormal_flag)
            
            if len(test_name) >= 3:
                lab_results.append({
                    "test_name": test_name,
                    "value": value,
                    "unit": unit,
                    "reference_range": ref_range,
                    "status": status
                })
                continue
    
    # Specific fallback extractions for tests that might be missed
    fallback_tests = extract_specific_tests_comprehensive(text)
    
    # Merge results, avoiding duplicates
    existing_test_names_lower = {test['test_name'].lower() for test in lab_results}
    for test in fallback_tests:
        if test['test_name'].lower() not in existing_test_names_lower:
            lab_results.append(test)
    
    return lab_results


def extract_specific_tests_comprehensive(text):
    """Extract specific tests using targeted patterns"""
    results = []
    
    # Liver Function Tests
    liver_tests = {
        "Total Bilirubin": (r'TOTAL\s+BILIRUBIN.*?([\d\.]+)', "mg/dl", "0.4-1.0"),
        "Direct Bilirubin": (r'DIRECT\s+BILIRUBIN.*?([\d\.]+)', "mg/dl", "0.1-0.5"),
        "Indirect Bilirubin": (r'INDIRECT\s+BILIRUBIN.*?([\d\.]+)', "mg/dl", "0.2-0.8"),
        "SGOT(AST)": (r'(?:SERUM\s+)?SGOT.*?([\d\.]+)', "IU/L", "5-40"),
        "SGPT(ALT)": (r'(?:SERUM\s+)?SGPT.*?([\d\.]+)', "IU/L", "5-55"),
        "Total Protein": (r'(?:SERUM\s+)?TOTAL\s+PROTEIN.*?([\d\.]+)', "gm/dl", "6.0-8.0"),
        "Albumin": (r'(?:SERUM\s+)?ALBUMIN.*?([\d\.]+)', "gm/dl", "3.5-5.5"),
        "Globulin": (r'(?:SERUM\s+)?GLOBULIN.*?([\d\.]+)', "gm/dl", "2.0-4.0"),
        "A/G Ratio": (r'A[/\\]G\s+RATIO.*?([\d\.]+(?::\d)?)', "RATIO", "1.0-1.85"),
        "Alkaline Phosphatase": (r'ALKALINE\s+PHOSPHAT[ES]+.*?([\d\.]+)', "IU/L", "up to 280"),
    }
    
    # CBC / Differential Count Tests
    cbc_tests = {
        "Platelet Count": (r'Platelet\s+count.*?([\d\.]+)', "Lakhs/Cumm", "2.1 - 5.0"),
        "Mean Cell Volume": (r'Mean\s+Cell\s+Volume.*?([\d\.]+)', "fL", "92 - 118"),
        "Mean Cell Haemoglobin": (r'Mean\s+Cell\s+Haemoglobin\s*\(MCH\).*?([\d\.]+)', "pg", "31 - 37"),
        "MCHC": (r'Mean\s+Cell\s+Haemoglobin\s+Concentration.*?([\d\.]+)', "g/L", "29 - 47"),
        "RDW": (r'RDW.*?([\d\.]+)', "%", "11.6 - 14.0"),
        "Neutrophils": (r'Neutrophils\.?\s+([\d\.]+)', "%", "20 - 45"),
        "Lymphocytes": (r'Lymphocytes\s+([\d\.]+)', "%", "28 - 35"),
        "Eosinophils": (r'Eosinophils\s+([\d\.]+)', "%", "1.4 - 4.3"),
        "Monocytes": (r'Monocytes\s+([\d\.]+)', "%", "4 - 7"),
        "Basophils": (r'Basophils\s+([\d\.]+)', "%", "0 - 1"),
    }
    
    # Combine all tests
    all_tests = {**liver_tests, **cbc_tests}
    
    for test_name, (pattern, unit, ref_range) in all_tests.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1)
            
            # Check for abnormal markers in surrounding context
            context_start = max(0, match.start() - 100)
            context_end = min(len(text), match.end() + 100)
            context = text[context_start:context_end]
            
            status = determine_status_from_markers(context, "")
            
            results.append({
                "test_name": test_name,
                "value": value,
                "unit": unit,
                "reference_range": ref_range,
                "status": status
            })
    
    return results


def clean_test_name(test_name):
    """Clean up test name"""
    # Remove method indicators
    test_name = re.sub(r'\(DPD\)|\(IFCC[^\)]*\)|Amp Buffer\)', '', test_name)
    # Remove extra spaces
    test_name = re.sub(r'\s+', ' ', test_name)
    # Remove trailing punctuation
    test_name = test_name.rstrip(':=.')
    return test_name.strip()


def determine_status_from_markers(text, abnormal_flag):
    """Determine test status from various markers"""
    # Check for arrow markers
    if '↑' in text or '↑' in abnormal_flag:
        return "High"
    if '↓' in text or '↓' in abnormal_flag:
        return "Low"
    
    # Check for *H *L markers
    if '*H' in text or '*H' in abnormal_flag:
        return "High"
    if '*L' in text or '*L' in abnormal_flag:
        return "Low"
    
    # Check for red color indicators (↑ symbol)
    if '↑' in text:
        return "High"
    if '↓' in text:
        return "Low"
    
    return "Normal"


def extract_diagnoses(text):
    """Extract medical conditions"""
    medical_keywords = [
        'diabetes', 'hypertension', 'anemia', 'liver disease', 
        'kidney disease', 'heart disease', 'hepatitis', 'cirrhosis',
        'infection', 'inflammation'
    ]
    
    diagnoses = []
    text_lower = text.lower()
    
    for keyword in medical_keywords:
        if keyword in text_lower:
            diagnoses.append({
                "condition": keyword.title(),
                "type": "Disease/Condition",
                "icd_code": None
            })
    
    return diagnoses


def extract_medications(text):
    """Extract medications"""
    medication_keywords = [
        'aspirin', 'metformin', 'warfarin', 'heparin', 'vitamin k',
        'paracetamol', 'antibiotic'
    ]
    
    medications = []
    text_lower = text.lower()
    
    for med in medication_keywords:
        if med in text_lower:
            medications.append({
                "medication_name": med.title(),
                "type": "Medication/Chemical"
            })
    
    return medications


def extract_all(text):
    """Main extraction function"""
    report_type = detect_report_type(text)
    
    return {
        "report_metadata": {
            "report_type": report_type,
            "department": "Auto-detected",
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_method": "Universal Pattern Matching"
        },
        "patient_information": extract_patient_info(text),
        "order_information": extract_order_info(text),
        "lab_tests": extract_lab_tests_universal(text),
        "diagnoses": extract_diagnoses(text),
        "medications": extract_medications(text),
        "clinical_notes": extract_clinical_interpretation(text)
    }


def detect_report_type(text):
    """Detect report type"""
    text_lower = text.lower()
    
    if 'differential count' in text_lower or 'neutrophils' in text_lower:
        return "Complete Blood Count (CBC) with Differential"
    elif 'liver function' in text_lower or 'lft' in text_lower or ('sgot' in text_lower and 'sgpt' in text_lower):
        return "Liver Function Test (LFT)"
    elif 'coagulation' in text_lower or ('pt' in text_lower and 'inr' in text_lower):
        return "Coagulation Panel"
    elif 'cbc' in text_lower or 'complete blood count' in text_lower:
        return "Complete Blood Count"
    else:
        return "General Laboratory Report"


def extract_clinical_interpretation(text):
    """Extract clinical notes"""
    patterns = [
        r'Remarks[:=]?\s*(.*?)(?:Liver|Magnesium|COAGULATION|Method|DIFFERENTIAL|$)',
        r'Interpretation[:=]?\s*(.*?)(?:Note|Method|$)',
        r'Comments[:=]?\s*(.*?)(?:Method|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match and match.group(1).strip():
            notes = match.group(1).strip()
            if len(notes) > 10 and notes != "PLEASE CORRELATE CLINICALLY.":
                return notes[:500]
    
    return None
