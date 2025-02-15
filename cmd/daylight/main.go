package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"text/template"
	"time"

	_ "time/tzdata"

	"golang.org/x/term"
	"github.com/fatih/color"

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

	var buf bytes.Buffer
	err = tmpl.Execute(&buf, templates.TodayTmplModel{
		Lat:  strconv.FormatFloat(latlong.Lat, 'g', 4, 64),
		Lng:  strconv.FormatFloat(latlong.Lng, 'g', 4, 64),
		Rise: daylight.LocalisedTime(suntimes.Rises, timezone),
		Sets: daylight.LocalisedTime(suntimes.Sets, timezone),
		Noon: daylight.FormatNoon(suntimes, timezone),
		Len:  daylight.FormatDayLength(suntimes),
		Diff: daylight.FormatLengthDiff(suntimes, yesterday),
		IP:   ipInfo.IP,
	})
	checkErr(err)

	var output string
	if prettyMode() {
		output = sunnify(buf.String())
	} else {
		output = buf.String()
	}

	fmt.Println(output)

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

// sunnify makes an input string... sunny
func sunnify(s string) string {
	lines := strings.Split(s, "\n")
	sunLines := strings.Split(templates.SunTxt, "\n")

	yellow := color.New(color.FgHiYellow, color.Bold)

  var output string
	for lineN, line := range lines {
    if lineN >= len(sunLines) {
			// "Picture" is complete, skip concatenations
      output = output + line + "\n"
			break
		}

		padding := 40 - len(line)
		if padding > 0 { // This should always be true, if not we'll get unpleasant ragged edges
      line = line + strings.Repeat(" ", padding)
		} 
    line = line + yellow.Sprint(sunLines[lineN])
		
		output = output + line + "\n"
	}

	return output
}


func checkErr(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
