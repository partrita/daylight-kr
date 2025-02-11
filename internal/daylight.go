package internal

import (
	"fmt"
	"github.com/nathan-osman/go-sunrise"
	"strconv"
	"strings"
	"time"
)

type LatLong struct {
	Lat float64
	Lng float64
}

type SunTimes struct {
	Rises      time.Time
	Sets       time.Time
	PolarNight bool
	PolarDay   bool
}

var nilTime = time.Time{}

func LocationToLatLong(loc string) (LatLong, error) {
	result := LatLong{}
	parseError := fmt.Errorf("cannot parse format of location data %q", loc)

	parts := strings.Split(loc, ",")
	if len(parts) != 2 {
		return result, parseError
	}

	lat, err := strconv.ParseFloat(parts[0], 64)
	if err != nil {
		return result, parseError
	}

	lng, err := strconv.ParseFloat(parts[1], 64)
	if err != nil {
		return result, parseError
	}

	result.Lat = lat
	result.Lng = lng
	return result, nil
}

// SunTimesForPlaceDate returns the sun rise / set times for the given lat/long in UTC.
// It also checks whether we are in polar day / polar night.
func SunTimesForPlaceDate(latlong LatLong, date time.Time) SunTimes {
	year, month, day := date.Date()

	rises, sets := sunrise.SunriseSunset(
		latlong.Lat, latlong.Lng,
		year, month, day,
	)

	polarDay := false
	polarNight := false

	// go-sunrise returns empty time.Time{} values if in polar day / night
	if rises == nilTime && sets == nilTime {
		isNorth := latlong.Lat >= 0
		isSouth := !isNorth

		isSummer := (month > time.March) && (month < time.October)
		isWinter := !isSummer

		fmt.Printf("isNorth %v, isSouth %v \n", isNorth, isSouth)

		switch {
		case isNorth && isSummer, isSouth && isWinter:
			{
				polarDay = true
			}

		case isNorth && isWinter, isSouth && isSummer:
			{
				polarNight = true
			}
		}
	}

	return SunTimes{
		Rises:      rises,
		Sets:       sets,
		PolarNight: polarNight,
		PolarDay:   polarDay,
	}
}

func LocalisedTime(t time.Time, tz *time.Location) string {
	return t.In(tz).Format("15:04 PM")
}
