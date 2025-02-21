package templates

import _ "embed"

//go:embed sun.txt
var SunTxt string

//go:embed today.go.tmpl
var TodayTmpl string
