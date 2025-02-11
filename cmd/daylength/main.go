package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

const ipinfoUrl = "https://ipinfo.io/json?inc=ip,city,country,loc"

type IPInfo struct {
	IP      string `json:"ip"`
	City    string `json:"city"`
	Country string `json:"country"`
	Loc     string `json:"loc"`
}

type LatLong struct {
	Lat  float64
	Long float64
}

func main() {
	log.SetPrefix("[daylength] ")
	log.SetFlags(0)

	ipInfo, err := fetchIPInfo()
	checkErr(err)

	fmt.Printf("response was %v\n", ipInfo)

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

// WIP
//func string2latlong(s string) (LatLong, error) {
//	parseErr := fmt.Sprintf("Failed to parse latlong, expected format 'NN.nnnn,NN.nnnn' but received %q\n", s)
//
//	parts := strings.Split(s, ",")
//	if len(parts) != 2 {
//		return LatLong{}, errors.New(parseErr)
//	}
//
//	lat, err := strconv.ParseFloat(parts[0], 64)
//	if err != nil {
//		log.Fatal(parseErr)
//	}
//	lng, err := strconv.ParseFloat(parts[1], 64)
//	if err != nil {
//		log.Fatal(parseErr)
//	}
//
//	return lat, lng
//}

func checkErr(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
