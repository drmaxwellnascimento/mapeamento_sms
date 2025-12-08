�#import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.distance import geodesic
import time
import os

# Configuration
INPUT_CSV = "Valter_Rocha (1).csv"
OUTPUT_XLSX = "resultado_geocodificacao_final.xlsx"
TARGET_UBS_NAME_QUERY = "valter de jesus"
UBS_REF_FILE = "UBS_REFERENCIA_LIMPO.csv"
USER_AGENT = "saude_municipio_app_v1"

def load_data():
    print("Loading data...")
    # Read UBS references
    if not os.path.exists(UBS_REF_FILE):
        raise FileNotFoundError(f"{UBS_REF_FILE} not found.")
    df_ubs = pd.read_csv(UBS_REF_FILE)
    
    # Read Addresses
    # Detecting delimiter for Valter_Rocha (1).csv - inspecting file showed ';', but let's be robust
    try:
        df_addr = pd.read_csv(INPUT_CSV, sep=';', encoding='utf-8')
    except:
        df_addr = pd.read_csv(INPUT_CSV, sep=',', encoding='utf-8')

    # Find Target UBS
    target_ubs = df_ubs[df_ubs['Nome_UBS'].str.contains(TARGET_UBS_NAME_QUERY, case=False, na=False)]
    
    if target_ubs.empty:
        raise ValueError(f"UBS matching '{TARGET_UBS_NAME_QUERY}' not found in {UBS_REF_FILE}")
    
    ubs_row = target_ubs.iloc[0]
    ubs_coords = (ubs_row['Latitude'], ubs_row['Longitude'])
    print(f"Target UBS Found: {ubs_row['Nome_UBS']} @ {ubs_coords}")
    
    return df_addr, ubs_coords, ubs_row['Nome_UBS']

def geocode_addresses(df, ubs_coords):
    geolocator = Nominatim(user_agent=USER_AGENT)
    
    # Define viewbox (approx 10km box around UBS for biasing)
    # 0.1 degree is roughly 11km
    viewbox_n = ubs_coords[0] + 0.1
    viewbox_s = ubs_coords[0] - 0.1
    viewbox_e = ubs_coords[1] + 0.1
    viewbox_w = ubs_coords[1] - 0.1
    
    # viewbox format: (Point(lat, lon), Point(lat, lon)) - South-West, North-East usually for Nominatim?
    # Actually Nominatim python doc says: viewbox=(Point1, Point2)
    
    results = []
    
    print(f"Starting geocoding for {len(df)} addresses...")
    
    for index, row in df.iterrows():
        original_addr = row['Endereco_Completo'] if 'Endereco_Completo' in row else str(row.iloc[-1]) # Fallback
        
        print(f"Processing ({index+1}/{len(df)}): {original_addr}")
        
        location = None
        found_address = "Não encontrado"
        lat = 0.0
        lon = 0.0
        distance = -1
        status = "NAO_ENCONTRADO"
        
        try:
            # Attempt 1: Direct search with viewbox
            location = geolocator.geocode(original_addr, viewbox=[(viewbox_s, viewbox_w), (viewbox_n, viewbox_e)], exactly_one=True, timeout=10)
            
            if not location:
                # Attempt 2: Try stripping excess commas or specific text if needed (simple retry logic)
                 # Maybe generic "Nossa Senhora do Socorro - SE" helps
                 pass
            
            if location:
                found_address = location.address
                lat = location.latitude
                lon = location.longitude
                
                # Calculate distance
                point_found = (lat, lon)
                distance = geodesic(ubs_coords, point_found).meters
                
                if distance > 3000:
                    status = "ALERTA_LONGE"
                else:
                    status = "CONFIRMADO"
            
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Error geocoding {original_addr}: {e}")
            status = "ERRO_CONEXAO"
        except Exception as e:
            print(f"Unexpected error: {e}")
            status = "ERRO_DESCONHECIDO"
            
        results.append({
            "Endereço Original": original_addr,
            "Endereço Encontrado": found_address,
            "Latitude": lat,
            "Longitude": lon,
            "Distância_da_UBS_Metros": round(distance, 2) if distance >= 0 else -1,
            "Status": status
        })
        
        time.sleep(1.2) # Mandatory pause
        
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        df_addresses, target_coords, target_name = load_data()
        
        df_results = geocode_addresses(df_addresses, target_coords)
        
        # Save to Excel
        print(f"Saving results to {OUTPUT_XLSX}...")
        df_results.to_excel(OUTPUT_XLSX, index=False)
        print("Done!")
        
    except Exception as e:
        print(f"Fatal Error: {e}")
�#*cascade082Jfile:///c:/Users/drmax/Documents/SECRETARIA/mapeamento/mapear_com_geopy.py