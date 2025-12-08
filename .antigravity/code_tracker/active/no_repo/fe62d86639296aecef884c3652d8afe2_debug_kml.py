…	from fastkml import kml

def list_features():
    try:
        with open('ubs.kml', 'rb') as f:
            doc = f.read()
        
        k = kml.KML()
        k.from_string(doc)
        
        features = list(k.features())
        print(f"Root features: {len(features)}")
        
        # Usually KML has a Document -> Folder -> Placemarks structure
        for feature in features:
            print(f"Feature: {feature.name} ({type(feature)})")
            if isinstance(feature, kml.Document) or isinstance(feature, kml.Folder):
                sub_features = list(feature.features())
                for sub in sub_features:
                    print(f"  Sub-Feature: {sub.name} ({type(sub)})")
                    if hasattr(sub, 'features'):
                        sub_sub = list(sub.features())
                        print(f"    found {len(sub_sub)} items inside {sub.name}")
                        for item in sub_sub[:5]: # just show first 5
                             print(f"      - {item.name}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_features()
…	*cascade082Cfile:///c:/Users/drmax/Documents/SECRETARIA/mapeamento/debug_kml.py