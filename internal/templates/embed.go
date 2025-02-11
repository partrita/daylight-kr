package templates

import _ "embed"

//go:embed today.go.tmpl
var TodayTmpl string

type TodayTmplModel struct {
	Lat  string
	Lng  string
	Rise string
	Sets string
	Noon string
	IP   string
	Len  string
	Diff string
}
