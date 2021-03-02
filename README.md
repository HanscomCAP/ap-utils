# ap-utils
Utilities for planning AP sorties

## csv2kml.py
Convert a CSV file containing photo targets into an equivalent KML file that can be imported into Google Earth or ForeFlight.

Usage:

```python csv2kml.pypyth <filename>```

The CSV file format is somewhat flexible, but it must have the following columns (names are case-insensitive):
* Task # or Imagery ID
* State
* Description
* Special Instructions (optional)
* Start Longitude
* Start Latitude

Task # / Imagery ID is the name that will be assigned to the waypoints.  The expected format is \<STATE>_\<ID>.  If \<STATE> is not included, the value in the State column will be used.

Description and Special Instructions (if specified) will be used as the Waypoint Description.

Longitute and Latitude should either be decimal degrees or DD MM SS.S H, where
* DD = Degrees
* MM = Minutes
* SS.S = Seconds
* H = Hemisphere (N/S for Latitude, E/W for Longitude)

### Notes

See https://developers.google.com/kml/documentation for complete documentation on the KML format.  For the purposes of this program, we only care about ```Placemark``` elements.  The output KML has the following structure:
``` XML
<kml>
	<Folder>
		<Placemark>
			<name>IDENTIFIER</name>
			<description>DESCRIPTION/INSTRUCTIONS</description>
			<Point>
				<coordinates>DECIMAL_LONGITUDE,DECIMAL_LATITUDE</coordinates>
			</Point>
		</Placemark>
        ...
	</Folder>
</kml>
```

### Samples

See targets.csv / targets.kml and mawg-targets.csv / mawg-targets.kml for example inputs and outputs.