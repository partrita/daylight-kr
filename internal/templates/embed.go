package templates

import _ "embed"

//go:embed today.go.tmpl
var TodayTmpl string

type TodayTmplModel struct {
	Lat               string
	Lng               string
	Date              string
	HHMM              string
	Rise              string
	Sets              string
	Len               string
	Diff              string
	Projected         string
	ProjectedDate     string
	ProjectedDistance string
	NextDawn          string
	Day               bool
	Rem               string
}
