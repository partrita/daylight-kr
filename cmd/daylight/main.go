package main

import (
	"bytes"
	"fmt"
	"log"
	"time"
	_ "time/tzdata"

	daylight "github.com/jbreckmckye/daylight/internal"
	templates "github.com/jbreckmckye/daylight/internal/templates"
)

func main() {
	log.SetPrefix("[daylength] ")
	log.SetFlags(0)

	ipInfo, err := daylight.FetchIPInfo()
	checkErr(err)

	latlong, err := daylight.LocationToLatLong(ipInfo.Loc)
	checkErr(err)

	timezone, err := time.LoadLocation(ipInfo.TZ)
	checkErr(err)

	now := time.Now().In(timezone)	
  viewmodel := daylight.TodayStats(now, timezone, latlong, ipInfo.IP)

	tmpl := templates.TodayTemplate()
	var buf bytes.Buffer
	err = tmpl.Execute(&buf, viewmodel)
	checkErr(err)

	var output string
	if daylight.UsePrettyMode() {
		output = daylight.Sunnify(buf.String())
	} else {
		output = buf.String()
	}

	fmt.Println(output)
}

func checkErr(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
