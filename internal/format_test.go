package internal

import (
	"testing"
	"time"
)

func TestFormatDayLength(t *testing.T) {
	type TestCase struct {
		SunTimes
		Want string
	}

	cases := []TestCase{
		{
			SunTimes: SunTimes{
				PolarDay:   true,
				PolarNight: false,
				Length:     0,
			},
			Want: "all day (polar sun)",
		},
		{
			SunTimes: SunTimes{
				PolarDay:   false,
				PolarNight: true,
				Length:     0,
			},
			Want: "none (polar night)",
		},
		{
			SunTimes: SunTimes{
				PolarDay:   false,
				PolarNight: false,
				Length:     (12 * time.Hour) + (34 * time.Minute) + (56 * time.Second),
			},
			Want: "12 hrs, 34 mins",
		},
		{
			SunTimes: SunTimes{
				PolarDay:   false,
				PolarNight: false,
				Length:     24 * time.Hour,
			},	
			Want: "24 hrs, 0 mins",
		},
	}

	for _, tc := range cases {
		got := FormatDayLength(tc.SunTimes)
		if got != tc.Want {
			t.Fatalf("expected %q but got %q, SunTimes=%v", tc.Want, got, tc.SunTimes)
		}
	}
}
