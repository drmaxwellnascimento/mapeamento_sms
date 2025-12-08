Àimport xml.etree.ElementTree as ET
import pandas as pd
import os

def analyze_kml(file_path):
    print(f"--- Analyzing {file_path} ---")
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # KML usually has a namespace
        namespace = ''
        if '}' in root.tag:
            namespace = root.tag.split('}')[0] + '}'
            
        placemarks = []
        # Search for Placemarks. They can be nested in Document/Folder
        for placemark in root.findall(f".//{namespace}Placemark"):
            name = placemark.find(f"{namespace}name")
            if name is not None:
                placemarks.append(name.text)
                
        print(f"Total Placemarks found: {len(placemarks)}")
        print("First 5 UBS names:")
        for name in placemarks[:5]:
            print(f"- {name}")
            
    except Exception as e:
        print(f"Error reading KML: {e}")

def analyze_csv(file_path):
    print(f"\n--- Analyzing {file_path} ---")
    try:
        # Try reading with different encodings if default fails, common in Brazil (latin1)
        try:
            df = pd.read_csv(file_path, encoding='utf-8', sep=';') # Try semi-colon first for BR CSVs
            if len(df.columns) <= 1: # If only 1 column, maybe it's comma separated
                 df = pd.read_csv(file_path, encoding='utf-8', sep=',')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1', sep=';')
            if len(df.columns) <= 1:
                 df = pd.read_csv(file_path, encoding='latin1', sep=',')

        print("Columns found:")
        for col in df.columns:
            print(f"- {col}")
            
        print("\nFirst row sample:")
        print(df.iloc[0].to_dict())
        
    except Exception as e:
        print(f"Error reading CSV: {e}")

if __name__ == "__main__":
    base_dir = r"c:\Users\drmax\Documents\SECRETARIA\mapeamento"
    kml_file = os.path.join(base_dir, "ubs.kml")
    csv_file = os.path.join(base_dir, "Valter_Rocha (1).csv")
    
    if os.path.exists(kml_file):
        analyze_kml(kml_file)
    else:
        print(f"File not found: {kml_file}")
        
    if os.path.exists(csv_file):
        analyze_csv(csv_file)
    else:
        print(f"File not found: {csv_file}")
À*cascade082Ffile:///c:/Users/drmax/Documents/SECRETARIA/mapeamento/analyze_data.py