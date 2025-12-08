ð

from lxml import etree
import os

def extract_placemarks(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        tree = etree.parse(file_path)
        root = tree.getroot()
        
        # Namespaces
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        # Find all Placemarks
        placemarks = root.findall('.//kml:Placemark', ns)
        
        results = []
        for pm in placemarks:
            name_elem = pm.find('kml:name', ns)
            name = name_elem.text if name_elem is not None else "Unnamed"
            
            # Find Point coordinates
            point = pm.find('.//kml:Point/kml:coordinates', ns)
            if point is not None and point.text:
                coords_str = point.text.strip()
                # format: lon,lat,z
                parts = coords_str.split(',')
                if len(parts) >= 2:
                    lon = parts[0]
                    lat = parts[1]
                    results.append({'name': name, 'lat': lat, 'lon': lon})
        
        print("UBS Encontradas:")
        for res in results:
            print(f"Nome: {res['name']} | Lat: {res['lat']}, Lon: {res['lon']}")
            
    except Exception as e:
        print(f"Error parsing KML: {e}")

extract_placemarks('ubs.kml')
ð
*cascade082Jfile:///c:/Users/drmax/Documents/SECRETARIA/mapeamento/extract_kml_lxml.py