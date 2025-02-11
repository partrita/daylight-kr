package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strconv"
	"text/template"
	"time"

	_ "time/tzdata"

	"golang.org/x/term"

	daylight "github.com/jbreckmckye/daylight/internal"
	templates "github.com/jbreckmckye/daylight/internal/templates"
)

type IPInfo struct {
	IP      string `json:"ip"`
	City    string `json:"city"`
	Country string `json:"country"`
	Loc     string `json:"loc"`
	TZ      string `json:"timezone"`
}

const ipinfoUrl = "https://ipinfo.io/json?inc=ip,city,country,loc,timezone"

func main() {
	log.SetPrefix("[daylength] ")
	log.SetFlags(0)

	ipInfo, err := fetchIPInfo()
	if err != nil {
		log.Printf("Error fetching data from %q\n", ipinfoUrl)
		log.Fatal(err)
	}

	// Testing

	//ipInfo = IPInfo{
	//	IP:      "any",
	//	City:    "cape town",
	//	Country: "south africa",
	//	Loc:     "-33.9258,18.4232",
	//	TZ:      "Africa/Johannesburg",
	//}

	//ipInfo = IPInfo{
	//	IP:      "any",
	//	City:    "svalbard",
	//	Country: "norway",
	//	Loc:     "77.8750,20.9752",
	//	TZ:      "Arctic/Longyearbyen",
	//}

	//ipInfo = IPInfo{
	//	IP:      "any",
	//	City:    "south pole",
	//	Country: "Antartica",
	//	Loc:     "-90,0",
	//	TZ:      "Antarctica/Rothera",
	//}

	latlong, err := daylight.LocationToLatLong(ipInfo.Loc)
	checkErr(err)

	timezone, err := time.LoadLocation(ipInfo.TZ)
	checkErr(err)

	now := time.Now().In(timezone)
	suntimes := daylight.SunTimesForPlaceDate(latlong, now)
	yesterday := daylight.SunTimesYesterday(latlong, now)

	tmpl, err := template.New("today").Parse(templates.TodayTmpl)
	checkErr(err)

	err = tmpl.Execute(os.Stdout, templates.TodayTmplModel{
		Lat:  strconv.FormatFloat(latlong.Lat, 'g', 4, 64),
		Lng:  strconv.FormatFloat(latlong.Lng, 'g', 4, 64),
		Rise: daylight.LocalisedTime(suntimes.Rises, timezone),
		Sets: daylight.LocalisedTime(suntimes.Sets, timezone),
		Noon: daylight.FormatNoon(suntimes, timezone),
		Len:  daylight.FormatDayLength(suntimes),
		Diff: daylight.FormatLengthDiff(suntimes, yesterday),
		IP:   ipInfo.IP,
	})

}

func fetchIPInfo() (IPInfo, error) {
	res, err := http.Get(ipinfoUrl)
	checkErr(err)
	defer func() {
		err = res.Body.Close()
		checkErr(err)
	}()

	decoder := json.NewDecoder(res.Body)
	result := IPInfo{}

	err = decoder.Decode(&result)
	return result, err
}

func prettyMode() bool {
	if !term.IsTerminal(0) {
		return false
	}

	width, _, err := term.GetSize(0)
	if err != nil {
		return false
	}

	if width < 80 {
		return false
	}

	return true
}

func checkErr(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
