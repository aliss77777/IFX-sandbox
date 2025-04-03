from xml.etree import ElementTree as ET
import pandas as pd

# Define the KML namespace
ns = {'kml': 'http://www.opengis.net/kml/2.2'}

# 1. Parse the KML file
tree = ET.parse("merged/data/temp_unzipped/doc.kml")
root = tree.getroot()

# 2. Find all Folder elements using the namespace
folders = root.findall(".//kml:Folder", ns)

# 3. Choose the second folder
# Print folder names to help identify the correct one
print("Available folders:")
for i, folder in enumerate(folders):
    name = folder.find(".//kml:name", ns)
    print(f"{i}: {name.text if name is not None else 'Unnamed folder'}")

interesting_folder = folders[1]  # You might want to adjust this index based on the output

# 4. For each Placemark, gather data
rows = []
for placemark in interesting_folder.findall(".//kml:Placemark", ns):
    row_data = {}
    
    # Get placemark name if available
    name = placemark.find(".//kml:name", ns)
    if name is not None:
        row_data['Name'] = name.text

    # ExtendedData -> Data elements
    extended_data = placemark.find(".//kml:ExtendedData", ns)
    if extended_data is not None:
        data_elements = extended_data.findall(".//kml:Data", ns)
        for data_el in data_elements:
            col_name = data_el.get("name")
            val_el = data_el.find(".//kml:value", ns)
            value = val_el.text if val_el is not None else None
            row_data[col_name] = value

    rows.append(row_data)

# Convert to DataFrame and save as CSV
df = pd.DataFrame(rows)
df.to_csv("merged/data/output.csv", index=False)

print(f"Processed {len(rows)} placemarks")
print("Output saved to merged/data/output.csv")
