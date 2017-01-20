## Region classer

Classes used to classify the regions in and around Romania into usefull tags.

## Usage

### Get classes for a particular point:

```
getRegionClasses(45.8, 25.2) == ['romania']
```

### Instantiate and use custom region classer:

```
rc =  RegionClasser(<path to shapefiles directory>)
rc.plotRegions()            # plot regions to screen for visual inspection
rc.getClasses(lat, lon)     # get regions containing this point
```

