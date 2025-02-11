package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"text/template"
	"time"

	"golang.org/x/term"
	_ "time/tzdata"

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
	checkErr(err)

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

	fmt.Printf("response was %v\n", ipInfo)
	latlong, err := daylight.LocationToLatLong(ipInfo.Loc)
	checkErr(err)

	fmt.Printf("latlong was %v\n", latlong)

	timezone, err := time.LoadLocation(ipInfo.TZ)
	checkErr(err)

	now := time.Now().In(timezone)
	suntimes := daylight.SunTimesForPlaceDate(latlong, now)

	fmt.Printf("rise %q, set %q\n", suntimes.Rises, suntimes.Sets)
	fmt.Printf("polar day %v, night %v\n", suntimes.PolarDay, suntimes.PolarNight)
	fmt.Printf("your local time for rise %q\n", daylight.LocalisedTime(suntimes.Rises, timezone))
	fmt.Printf("your local time for set %q\n", daylight.LocalisedTime(suntimes.Sets, timezone))

	pretty := prettyMode()
	fmt.Printf("should use pretty mode? %v\n", pretty)
	print(".......\n")

	tmpl, err := template.New("today").Parse(templates.TodayTmpl)
	checkErr(err)

	err = tmpl.Execute(os.Stdout, templates.TodayTmplModel{
		Lat:               strconv.FormatFloat(latlong.Lat, 'g', 4, 64),
		Lng:               strconv.FormatFloat(latlong.Lng, 'g', 4, 64),
		Date:              now.Format("Jan 02"),
		HHMM:              now.Format("15:04 PM"),
		Rise:              suntimes.Rises.Format("15:04 PM"),
		Sets:              suntimes.Sets.Format("15:04 PM"),
		Len:               "<length>",
		Diff:              "<diff>",
		Projected:         "<1hr longer/1hr shorter/longest day/shortest day>",
		ProjectedDate:     "<when>",
		ProjectedDistance: "<(expleened)>",
		NextDawn:          "<next dawn>",
		Day:               true,
		Rem:               "<remaining>",
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
