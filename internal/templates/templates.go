package templates

import (
	_ "embed"
	"log"
	"text/template"
)

//go:embed sun.txt
var SunTxt string

//go:embed today.go.tmpl
var todayTmpl string

func TodayTemplate() *template.Template {
	tmpl, err := template.New("today").Parse(todayTmpl)
	if err != nil {
		log.Fatalf("Couldn't load template, err %q", err.Error())
	}

	return tmpl
}
