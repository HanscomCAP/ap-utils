import sys
import os
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

# Convert a DMS string into decimal degrees allowing either ' ' or '-' as delimiters.
# Assume N and W hemispheres unless specified otherwise.
def convertDMS(dms):
    dms = dms.strip('Â ').split(' ')
    for item in dms:
        if (item == ''):
            dms.remove(item)
    if (len(dms) == 0):
        d = m = s = h = 0
    elif (len(dms) == 2):
        d, m, s = dms[0].split('-')
        d = float(d)
        m = float(m)
        s = float(s)
        h = dms[1]
    else:
        d, m, s, h = dms
        d = float(d.strip("Â°" + "'" + '"'))
        m = float(m.strip("Â°" + "'" + '"'))
        s = float(s.strip("Â°" + "'" + '"'))
    result = d + m/60.0 + s/3600
    if (h == 'W') or (h == 'S'):
        result = -result
    return result


# This can handle coordinates in either decimal degrees or one of a few DMS formats.
# If lon is a positive decimal value, assume it's a typo and change it to negative (Western hemisphere)
# If either coordinate is not a decimal value, treat it as DMS and use convertDMS to get a decimal.
def MakeCoordinates(lon, lat):
    if (isfloat(lon)):
        lon = float(lon)
        if (lon > 0):
            print('Fixing lon: ' + str(lon))
            lon = -lon
    else:
        lon = convertDMS(lon)
    
    if (isfloat(lat)):
        lat = float(lat)
    else:
        lat = convertDMS(lat)

    return str(lon) + ',' + str(lat)

# This attempts to generate a standardized name using the target id and state name, accounting for observed variability in input formats
# If the name has two or more parts, use the first two parts.  If it has only one part, prepend the value from the State column
def MakeStandardName(name, state):
    parts = name.split('_')
    if (len(parts) > 1):
        return parts[0] + '_' + parts[1]
    return state.strip(' ') + '_' + name

def MakePlacemark(folder, name, description, longitude, latitude):
    placemark = ET.SubElement(folder, 'Placemark')
    ET.SubElement(placemark, 'name').text = name
    ET.SubElement(placemark, 'description').text = description
    point = ET.SubElement(placemark, 'Point')
    ET.SubElement(point, 'coordinates').text = MakeCoordinates(longitude, latitude)
    return placemark

def ProcessFile(filename):
    kml = ET.Element('kml', {'xmlns': 'http://www.opengis.net/kml/2.2'})
    # The XML document uses a Folder element containing a number of Placemark elements. Here we create the Folder.
    folder = ET.SubElement(kml, 'Folder', {
        'xmlns:gx': 'http://www.google.com/kml/ext/2.2',
        'xmlns:atom': 'http://www.w3.org/2005/Atom',
        'xmlns': 'http://www.opengis.net/kml/2.2'} )

    with open(filename, newline='') as targets:
        targetreader = csv.reader(targets, delimiter=',', quotechar='"')
        firstrow = True
        for row in targetreader:
            if (firstrow):
                # Figure out which columns have the data we need
                # This provides some flexibility on the layout of the input file as long as the columns use these names
                colNum = 0
                for heading in row:
                    heading = heading.lower()
                    if (heading.startswith('task') or heading.startswith('id') or heading == 'imagery id'):
                        idCol = colNum
                    elif (heading == 'state'):
                        stateCol = colNum
                    elif (heading == 'description'):
                        descCol = colNum
                    elif (heading == 'special instructions'):
                        instCol = colNum
                    elif (heading == 'start longitude'):
                        startLongCol = colNum
                    elif (heading == 'start latitude'):
                        startLatCol = colNum
                    elif (heading == 'stop longitude'):
                        stopLongCol = colNum
                    elif (heading == 'stop latitude'):
                        stopLatCol = colNum
                    colNum += 1
                firstrow = False
                continue
            # Add one Placemark for every row beyond the first.
            # Each Placemark has this form:
            # <Placemark>
            #    <name>NAME</name>
            #    <description>DESCRIPTION</description>
            #    <Point><coordinates>LONG,LAT</coordinates></Point>
            # </Placemark>
            name = MakeStandardName(row[idCol], row[stateCol])
            description = row[descCol]
            if (row[instCol] != ''):
                description = description + '\n' + row[instCol]

            if (row[stopLongCol].replace("\xc2\xa0", " ").strip(' ') == ''): # Empty string or spaces only => Single Waypoint
                MakePlacemark(folder, name, description, row[startLongCol], row[startLatCol])
            else: # Start and Stop Waypoints
                MakePlacemark(folder, name + '_START', description, row[startLongCol], row[startLatCol])
                MakePlacemark(folder, name + '_STOP', description, row[stopLongCol], row[stopLatCol])

    dom = minidom.parseString(ET.tostring(kml))
    kmlfilename = os.path.splitext(filename)[0] + '.kml'
    print('Writing KML to ' + kmlfilename)
    kmlfile = open(kmlfilename, "wb")
    kmlfile.write(dom.toprettyxml(encoding='UTF-8'))


if (len(sys.argv) < 2):
    print('Usage: python ' + sys.argv[0] + ' [csvfilename]' )
    quit()

ProcessFile(sys.argv[1]) # mawg-targets.csv
