package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
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

	latlong, err := daylight.LocationToLatLong(ipInfo.Loc)
	checkErr(err)

	timezone, err := time.LoadLocation(ipInfo.TZ)
	checkErr(err)

	now := time.Now().In(timezone)
	source := fmt.Sprintf("IP address (%s)", ipInfo.IP)
	
  viewmodel := daylight.TodayStats(now, timezone, latlong, source)

	tmpl := parseTemplate("today", templates.TodayTmpl)

	var buf bytes.Buffer
	err = tmpl.Execute(&buf, viewmodel)
	checkErr(err)

	var output string
	if prettyMode() {
		output = daylight.Sunnify(buf.String())
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

func parseTemplate(name string, src string) *template.Template {
	tmpl, err := template.New(name).Parse(src)
	if err != nil {
		log.Fatalf("Couldn't load template, error %q", err.Error())
	}
	return tmpl
}

func checkErr(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
