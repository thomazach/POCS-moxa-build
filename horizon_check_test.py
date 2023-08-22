import math

from datetime import datetime
from datetime import timezone

from astropy.coordinates import EarthLocation, SkyCoord, AltAz, Angle, get_body
from astropy.time import Time
from astropy import units as u

### Functions to put into core after taijen pushes changes
### Need a config file with front end for inputting lat lon elevation 
def convertRaDecToAltAZ(skyCoord, location):
    observationTime = Time(datetime.now(timezone.utc))
    localFrame = AltAz(location=location, obstime=observationTime)

    return skyCoord.transform_to(localFrame)

def astronomicalNight(unitLocation):
    sun = get_body('sun', Time(datetime.now(timezone.utc)))
    sunAltAz = convertRaDecToAltAZ(sun, unitLocation)

    if float(sunAltAz.alt.deg) < -18:
        return True

    print("It isn't astronomical night yet.")
    return False

def aboveHorizon(targetSkyCoord, unitLocation):
    targetAltAz = convertRaDecToAltAZ(targetSkyCoord, unitLocation)
    
    if float(targetAltAz.alt.deg) < 0:
        print("Target is below the horizon.")
        return False
    return True

    
def moonObstruction(targetSkyCoord):
    current_time = Time(datetime.now(timezone.utc))
    moon = get_body('moon', current_time)

    # Need to calculate lunar phase percentage to determine level of avoidance
    ### Adapted from astroplan: https://github.com/astropy/astroplan/blob/main/astroplan/moon.py (8/3/2023)
    sun = get_body('sun', current_time)
    seperation = float(sun.separation(moon).rad)
    sunDistance = float(sun.distance.au)
    lunar_orbital_phase_rad = math.atan2(sunDistance * math.sin(seperation), float(moon.distance.au) - sunDistance * math.cos(seperation))
    percent_illuminated = (1 + math.cos(lunar_orbital_phase_rad))/2

    # Never try to look at something through the moon, and look further away from the moon the brighter it is
    moonRadius = Angle("34.1'") / 2
    moonAvoidanceRadius = moonRadius + percent_illuminated * Angle(60, u.deg)
    target_ra, target_dec = (float(targetSkyCoord.ra.rad), float(targetSkyCoord.dec.rad))
    moon_ra, moon_dec = (float(moon.ra.rad), float(moon.dec.rad))
    # Angular distance between two points on a sphere
    angular_diff = math.acos(math.sin(moon_dec) * math.sin(target_dec) + math.cos(moon_dec) * math.cos(target_dec) * math.cos(target_ra - moon_ra))

    if angular_diff < moonAvoidanceRadius.rad:
        print("Current target obstructed by moon.")
        return False
    
    return True

def checkTargetAvailability(position, unitLocation):
    checkFunctions = [(astronomicalNight, [unitLocation]),
                      (aboveHorizon, [SkyCoord(position, unit=(u.hourangle, u.deg)), unitLocation]),
                      (moonObstruction, [SkyCoord(position, unit=(u.hourangle, u.deg))])
    ]

    for func, args in checkFunctions:
        if not func(*args):
            return False
    return True

def main():
    LAT_CONFIG = '44.56725'
    LON_CONFIG = '-123.28925'
    ELEVATION_CONFIG = 71.628
    UNIT_LOCATION = EarthLocation(lat=LAT_CONFIG, lon=LON_CONFIG, height=ELEVATION_CONFIG * u.m)
    
    TEST_POSITION ='01 46 06.5 -07d30m40.7s'

    _ = checkTargetAvailability(TEST_POSITION, UNIT_LOCATION)
    print(_)

if __name__ == "__main__":
    main()


