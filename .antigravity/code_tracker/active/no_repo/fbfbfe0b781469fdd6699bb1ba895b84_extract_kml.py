¿
from fastkml import kml
import os

def extract_placemarks(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'rb') as f:
        doc = f.read()

    k = kml.KML()
    k.from_string(doc)
    
    placemarks = []

    def recursive_parse(features, depth=0):
        indent = "  " * depth
        # Handle if features is a generator or list
        try:
            # If it's a method calling it might be needed, if list it's iterable
            # We suspect it is a list based on k.features
            # But let's handle case where it might be a method? No, let's just assume list/iterable property first from previous error
            # If features is just an object, try to iterate
            iterator = features
            
            for feature in iterator:
                print(f"{indent}Found feature type: {type(feature)}")
                if isinstance(feature, kml.Placemark):
                    name = feature.name
                    print(f"{indent}  - Name: {name}")
                    if feature.geometry:
                        try:
                            # Try standard shapely/geoif access
                            # Point might have .x .y or .coords
                            if hasattr(feature.geometry, 'coords'):
                                coords = feature.geometry.coords
                                lon, lat = coords[0][0], coords[0][1]
                                placemarks.append({'name': name, 'lat': lat, 'lon': lon})
                            else:
                                print(f"{indent}    No coords attribute on geometry: {type(feature.geometry)}")
                        except Exception as ge:
                            print(f"{indent}    Error getting coords: {ge}")
                elif isinstance(feature, kml.Folder) or isinstance(feature, kml.Document):
                    print(f"{indent}  - Recursing into container")
                    # Try accessing features property
                    # In some versions it is .features() method, in others .features property
                    # If k.features was a list, likely this is too
                    try:
                        sub_features = feature.features
                        # If it is a method, this will be the method object, not iterable (unless we call it)
                        # But previous error said 'list' object not callable, so k.features WAS a list.
                        # So feature.features should be a list too.
                        recursive_parse(sub_features, depth + 1)
                    except AttributeError:
                        # Fallback if it is a method? 
                        try:
                            recursive_parse(feature.features(), depth + 1)
                        except:
                            print(f"{indent}    Could not access features")
        except TypeError as e:
            print(f"{indent}Error iterating features: {e}")

    # Start with k.features (property as discovered)
    print("Starting parse...")
    recursive_parse(k.features)

    print("\nUBS Encontradas:")
    for pm in placemarks:
        print(f"Nome: {pm['name']} | Lat: {pm['lat']}, Lon: {pm['lon']}")

extract_placemarks('ubs.kml')
‹ *cascade08‹Â*cascade08ÂÒ *cascade08Òö*cascade08öõ *cascade08õ±*cascade08±¥ *cascade08¥⁄*cascade08⁄€ *cascade08€‰*cascade08‰Â *cascade08ÂÎ*cascade08ÎÏ *cascade08ÏÛ*cascade08ÛÙ *cascade08ÙØ*cascade08Ø∞ *cascade08∞ˇ*cascade08ˇÉ *cascade08ÉÉ*cascade08ÉÖ *cascade08Ö¥*cascade08¥º *cascade08ºÔ*cascade08ÔÚ *cascade08ÚΩ*cascade08ΩÇ *cascade08ÇÑ*cascade08Ñä *cascade08äã*cascade08ãå *cascade08åç*cascade08çé *cascade08éè*cascade08èê *cascade08êë*cascade08ëí *cascade08íò*cascade08òö *cascade08öû*cascade08ûÆ *cascade08Æ±*cascade08±≤ *cascade08≤∫*cascade08∫ª *cascade08ªæ*cascade08æø *cascade08ø¡*cascade08¡¬ *cascade08¬√*cascade08√ƒ *cascade08ƒ≈*cascade08≈∆ *cascade08∆…*cascade08…Õ *cascade08Õ–*cascade08–“ *cascade08“‘*cascade08‘‰ *cascade08‰Ê*cascade08Êê	 *cascade08ê	í	*cascade08í	ó	 *cascade08ó	ö	*cascade08ö	∏	 *cascade08∏	ª	*cascade08ª	Ω	 *cascade08Ω	ƒ	*cascade08ƒ	Ã	 *cascade08Ã	Õ	*cascade08Õ	—	 *cascade08—	÷	*cascade08÷	Ÿ	 *cascade08Ÿ	ﬂ	*cascade08ﬂ	‡	 *cascade08‡	„	*cascade08„	˜	 *cascade08˜	˙	*cascade08˙	˚	 *cascade08˚	˛	*cascade08˛	ˇ	 *cascade08ˇ	Ñ
*cascade08Ñ
Ö
 *cascade08Ö
Ü
*cascade08Ü
á
 *cascade08á
à
*cascade08à
â
 *cascade08â
ä
*cascade08ä
ã
 *cascade08ã
ê
*cascade08ê
í
 *cascade08í
ì
*cascade08ì
ú
 *cascade08ú
£
*cascade08£
∑
 *cascade08∑
∏
*cascade08∏
ª
 *cascade08ª
÷
*cascade08÷
‹
 *cascade08‹
ﬁ
*cascade08ﬁ
·
 *cascade08·
Á
*cascade08Á
ˇ
 *cascade08ˇ
Ä*cascade08Äà *cascade08àâ*cascade08âä *cascade08äé*cascade08éè *cascade08èô*cascade08ôö *cascade08ö£*cascade08£Ç *cascade08Çä*cascade08ä— *cascade08—Ë*cascade08Ëƒ *cascade08ƒ…*cascade08…  *cascade08 ›*cascade08›„ *cascade08„Ú*cascade08ÚÛ *cascade08Ûí*cascade08íì *cascade08ìó*cascade08óò *cascade08òú*cascade08ú£ *cascade08£‹*cascade08‹Á *cascade08Áå*cascade08åí *cascade08í¢*cascade08¢§ *cascade08§¶*cascade08¶ß *cascade08ßÆ*cascade08ÆØ *cascade08ØŒ*cascade08Œ– *cascade08–Ê*cascade08ÊÁ *cascade08ÁÏ*cascade08ÏÌ *cascade08Ìä*cascade08äã *cascade08ãè*cascade08èë *cascade08ëõ*cascade08õ£ *cascade08£±*cascade08±¥ *cascade08¥∑*cascade08∑∏ *cascade08∏ª*cascade08ªΩ *cascade08Ω *cascade08 À *cascade08Àı*cascade08ıˆ *cascade08ˆ˜*cascade08˜¯ *cascade08¯ô*cascade08ôö *cascade08öù*cascade08ùû *cascade08û¨*cascade08¨≠ *cascade08≠∏*cascade08∏∫ *cascade08∫ª*cascade08ªº *cascade08º·*cascade08·„ *cascade08„Ê*cascade08ÊË *cascade08Ë£*cascade08£§ *cascade08§´*cascade08´¨ *cascade08¨Æ*cascade08Æ∞ *cascade08∞ƒ*cascade08ƒ» *cascade08» *cascade08 ¢*cascade08¢≤ *cascade08≤π*cascade08π¬ *cascade08¬œ*cascade08œ÷ *cascade08÷Ë*cascade08ËÈ *cascade08ÈÍ*cascade08ÍÎ *cascade08Îë*cascade08ëì *cascade08ì®*cascade08®© *cascade08©´*cascade08´¨ *cascade08¨Ã*cascade08ÃÕ *cascade08ÕŒ*cascade08Œœ *cascade08œ“*cascade08“” *cascade08”‹*cascade08‹› *cascade08›ﬁ*cascade08ﬁ‰ *cascade08‰Ï*cascade08ÏÙ *cascade08Ùˇ*cascade08ˇÄ *cascade08ÄÅ*cascade08ÅÇ *cascade08ÇÑ*cascade08ÑÖ *cascade08Öã*cascade08ãò *cascade08ò¨*cascade08¨Æ *cascade08Æ∞*cascade08∞∫ *cascade08∫ª*cascade08ªº *cascade08º“*cascade08“” *cascade08”Ò*cascade08Òì *cascade08ì£ *cascade08£•*cascade08•¿ *cascade082Efile:///c:/Users/drmax/Documents/SECRETARIA/mapeamento/extract_kml.py