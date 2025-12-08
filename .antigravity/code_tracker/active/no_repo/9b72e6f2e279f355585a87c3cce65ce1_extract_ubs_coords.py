§import csv
from lxml import etree
import os

def extract_ubs_data(kml_file, output_csv):
    tree = etree.parse(kml_file)
    root = tree.getroot()
    
    # Handle namespaces
    namespaces = root.nsmap
    # If generic namespace is None, it might be tricky in xpath, but usually KML has a namespace like http://www.opengis.net/kml/2.2
    # We can use local-name() to avoid namespace issues or register the namespace.
    
    # Let's try to find the specific Folder using xpath with local-name() to be safe against namespace variations
    # We look for a Folder that has a name 'UBS - Nossa Senhora do Socorro'
    
    target_folder_name = "UBS - Nossa Senhora do Socorro"
    
    # XPath to find the folder. 
    # //*:Folder[*:name='UBS - Nossa Senhora do Socorro']
    # But checking text content is safer
    
    folders = root.xpath(f"//*[local-name()='Folder'][*[local-name()='name' and text()='{target_folder_name}']]")
    
    if not folders:
        print(f"Folder '{target_folder_name}' not found. Listing all folders found:")
        all_folders = root.xpath("//*[local-name()='Folder']/*[local-name()='name']")
        for f in all_folders:
            print(f" - {f.text}")
        return

    target_folder = folders[0]
    placemarks = target_folder.xpath(".//*[local-name()='Placemark']")
    
    print(f"Found {len(placemarks)} placemarks in '{target_folder_name}'.")
    
    data = []
    
    for pm in placemarks:
        name_node = pm.xpath("*[local-name()='name']")
        name = name_node[0].text if name_node else "Unknown"
        
        # Coordinates are usually in Point/coordinates
        coords_node = pm.xpath(".//*[local-name()='coordinates']")
        
        lat = ""
        lon = ""
        
        if coords_node:
            coords_text = coords_node[0].text.strip()
            # KML coordinates: lon,lat,alt
            parts = coords_text.split(',')
            if len(parts) >= 2:
                lon = parts[0]
                lat = parts[1]
        
        data.append([name, lat, lon])
        
    # Save to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Nome_UBS', 'Latitude', 'Longitude'])
        writer.writerows(data)
        
    print(f"Successfully exported {len(data)} records to {output_csv}")

if __name__ == "__main__":
    kml_file = 'Mapeamento de √Åreas de Sa√∫de - Nossa Senhora do Socorro (1).kml'
    output_csv = 'UBS_REFERENCIA_LIMPO.csv'
    
    if not os.path.exists(kml_file):
        print(f"Error: {kml_file} not found.")
    else:
        extract_ubs_data(kml_file, output_csv)
ú *cascade08úØ*cascade08Ø∞ *cascade08∞Ÿ*cascade08Ÿ§ *cascade082Lfile:///c:/Users/drmax/Documents/SECRETARIA/mapeamento/extract_ubs_coords.py