import fiona
from shapely.geometry import Point, MultiPolygon, shape
from shapely.ops import cascaded_union
import os


class RegionClasser(object):
    '''
    classify a point into a region tag
    '''

    def __init__(self, shapefiles_dir):
        """
            path to directory containing required shapefiles:
                ROU_adm1.shp    - romania counties
                iho.shp         - black sea shapefiles
        """
        self.shapefiles_dir = shapefiles_dir
        self.region_cache = dict()
        self.cache_loaded = False
        self.region_classes = dict()

    # array access. Call one of the getRegion* functions
    def __getitem__(self, key):
        key = 'getRegion'+key.title().replace('_', '')
        try:
            return self.region_cache[key]
        except KeyError:
            try:
                method = getattr(self, key)
            except AttributeError:
                return None

            self.region_cache[key] = method()
            return self.region_cache[key]

    def getRegionRomania(self):
        sf = fiona.open(os.path.join(self.shapefiles_dir, 'romania/ROU_adm1.shp'))
        rez = []
        for pol in sf:
            shp = shape(pol['geometry'])
            if pol['properties']['NAME_1'] in ['Ilfov', 'Bucharest']:
                shp = shp.buffer(0.2)
            rez.append(shp)
        rez = cascaded_union(rez)
        return (rez, 'romania')

    def getRegionBlackSea(self):
        sf = fiona.open(os.path.join(self.shapefiles_dir, 'black_sea/iho.shp'))
        rez = []
        for pol in sf:
            shp = shape(pol['geometry'])
            rez.append(shp)
        rez = cascaded_union(rez)
        return (MultiPolygon([rez]), 'black_sea')

    def getRegionBlackSeaBuffer(self):
        return (MultiPolygon([self['black_sea'][0].buffer(1.35).difference(self['black_sea'][0])]), 'black_sea_buffer')

    def getRegionRomaniaBuffer(self):
        return (MultiPolygon([self['romania'][0].buffer(1).difference(self['romania'][0])]), 'romania_buffer')

    def loadCache(self):
        '''
        Preload the cache with all the available regions by calling the appropriate functions
        '''
        for attr in dir(self):
            if attr.startswith('getRegion'):
                self.region_cache[attr] = getattr(self, attr)()
        self.cache_loaded = True

    def getClasses(self, lat, lon):
        if self.cache_loaded is False:
            self.loadCache()
        region_classes = []
        point = Point(lon, lat)
        for key, (multipoly, tag) in self.region_cache.iteritems():
            if multipoly.contains(point):
                region_classes.append(tag)
        return region_classes

    def plotRegions(self):
        import matplotlib.pyplot as plt
        from matplotlib.collections import PatchCollection
        from descartes import PolygonPatch
        '''
        visually check regions
        '''
        if self.cache_loaded is False:
            self.loadCache()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        all = cascaded_union([self.region_cache[key][0] for key in self.region_cache])
        minx, miny, maxx, maxy = all.bounds
        w, h = maxx - minx, maxy - miny
        ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
        ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
        ax.set_aspect(1.2)
        # ax.add_patch(PolygonPatch(all, fc='green', ec='#555555', alpha=1, zorder=1))

        for key, (multipoly, tag) in self.region_cache.iteritems():
            patches = PatchCollection([PolygonPatch(p, fc='yellow', ec='k', alpha=1) for p in multipoly], match_original=True)
            # patches.set_zorder(10)
            ax.add_collection(patches)

        plt.show()


class RomaniaUATClasser(object):
    pass

__rc = None  # Own instance of RegionClasser used by standalone functions
__me = os.path.abspath(os.path.dirname(__file__))


def getRegionClasses(lat, lon):
    global __rc, __me
    try:
        return __rc.getClasses(lat, lon)
    except AttributeError:
        __rc = RegionClasser(os.path.join(__me, 'shapefiles/'))
        return __rc.getClasses(lat, lon)

if __name__ == '__main__':
    '''
    self tests
    '''

    assert getRegionClasses(45.8, 25.2) == ['romania']

    rc = RegionClasser(os.path.join(__me, 'shapefiles/'))
    rc.loadCache()
    rc.plotRegions()

    assert rc.getClasses(45.8, 25.2) == ['romania']
    assert rc.getClasses(43.3, 23.8) == ['romania_buffer']
    assert rc.getClasses(40.9, 31.2) == ['black_sea_buffer']
    assert rc.getClasses(43.3, 30.1) == ['black_sea']

    result = rc.getClasses(43.6, 27.8)
    assert len(result) == 2
    assert 'romania_buffer' in result
    assert 'black_sea_buffer' in result

    result = rc.getClasses(45.03, 28.7)
    assert len(result) == 2
    assert 'black_sea_buffer' in result
    assert 'romania' in result

    result = rc.getClasses(44.27, 29.01)
    assert len(result) == 2
    assert 'romania_buffer' in result
    assert 'black_sea' in result
