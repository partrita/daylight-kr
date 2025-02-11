package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"
	"net/http"

	_ "time/tzdata"

	daylight "github.com/jbreckmckye/daylight/internal"
	sunrise "github.com/nathan-osman/go-sunrise"
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

	fmt.Printf("response was %v\n", ipInfo)
	latlong, err := daylight.LocationToLatLong(ipInfo.Loc)
	checkErr(err)

	fmt.Printf("latlong was %v\n", latlong)

	timezone, err := time.LoadLocation("Canada/Eastern") // should be time.LoadLocation(ipInfo.TZ) but for testing
	checkErr(err)

	// This will get the sunrise / sunset times in UTC
	rise, set := sunrise.SunriseSunset(
    43.65, -79.38,          // Toronto, CA
    2000, time.January, 1,  // 2000-01-01
  )
	fmt.Printf("rise %q, set %q\n", rise, set)
	fmt.Printf("your local time for rise %q\n", rise.In(timezone))
	fmt.Printf("your local time for set %q\n", set.In(timezone))

	// put into https://github.com/nathan-osman/go-sunrise
	// print
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

func checkErr(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
