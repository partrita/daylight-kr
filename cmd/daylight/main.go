package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	_ "time/tzdata"

	daylight "github.com/jbreckmckye/daylight/internal"
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

	fmt.Printf("response was %v\n", ipInfo)
	latlong, err := daylight.LocationToLatLong(ipInfo.Loc)
	checkErr(err)

	fmt.Printf("latlong was %v\n", latlong)

	timezone, err := time.LoadLocation(ipInfo.TZ)
	checkErr(err)

	suntimes := daylight.SunTimesForPlaceDate(latlong, time.Now().In(timezone))

	fmt.Printf("rise %q, set %q\n", suntimes.Rises, suntimes.Sets)
	fmt.Printf("polar day %v, night %v\n", suntimes.PolarDay, suntimes.PolarNight)
	fmt.Printf("your local time for rise %q\n", daylight.LocalisedTime(suntimes.Rises, timezone))
	fmt.Printf("your local time for set %q\n", daylight.LocalisedTime(suntimes.Sets, timezone))

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
