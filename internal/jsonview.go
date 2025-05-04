package internal

import (
	"encoding/json"
	"fmt"
)

// CondensedView supports a more succinct display mode
type JsonView struct {
	Rises  string `json:"rises"`
	Noon   string `json:"noon"`
	Sets   string `json:"sets"`
	Length string `json:"length"`
	Change string `json:"change"`
	Lat    string `json:"latitude"`
	Lng    string `json:"longitude"`
	Zone   string `json:"timezone"`
}

func (j JsonView) FormatString() (string, error) {
  b, err := json.MarshalIndent(j, "", "  ")
	if err != nil {
		return "", err
	}

	return string(b), nil
}

func JsonSummary(query DaylightQuery) JsonView {
	location := LatLong{
		Lat: query.Lat,
		Lng: query.Long,
	}

	today := SunTimesForPlaceDate(
		location,
		query.Date,
	)

	yesterday := SunTimesForPlaceDate(
		location,
		query.Date.AddDate(0, 0, -1),
	)

	return JsonView{
		Rises:  FormatRises(today, &query.TZ),
		Noon:   FormatNoon(today, &query.TZ),
		Sets:   FormatSets(today, &query.TZ),
		Length: FormatDayLength(today),
		Change: FormatLengthDiff(today, yesterday),
		Lat:    fmt.Sprintf("%f", query.Lat),
		Lng:    fmt.Sprintf("%f", query.Long),
		Zone:   query.TZ.String(),
	}
}
