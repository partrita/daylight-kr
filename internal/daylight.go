package internal

import (
	"fmt"
	"strconv"
	"strings"
)

type LatLong struct {
	Lat  float64
	Lng  float64
}

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
