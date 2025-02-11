package internal

import (
	"fmt"
)

func FormatDayLength(s SunTimes) string {
	if s.PolarDay {
		return "all day (polar sun)"
	}

	if s.PolarNight {
		return "none (polar night)"
	}

	inSeconds := DurationSeconds(s)
	inMinutes := inSeconds / 60

	hours := inMinutes / 60
	mins := inMinutes - (hours * 60)

	return fmt.Sprintf("%d hrs, %d mins", hours, mins)
}

func FormatLengthDiff(today SunTimes, yesterday SunTimes) string {
	lengthToday := DurationSeconds(today)
	lengthYesterday := DurationSeconds(yesterday)

	direction := 0
	if lengthToday > lengthYesterday {
		direction = 1
	}
	if lengthToday < lengthYesterday {
		direction = -1
	}

	if direction == 0 {
		return "the same as yesterday"
	}

	prefix := "+"
	if direction == -1 {
		prefix = "-"
	}

	diff := lengthToday - lengthYesterday
	if diff < 0 {
		diff = diff * -1
	}
	mins := diff / 60
	secs := diff - (mins * 60)

	return fmt.Sprintf("%s%dm %ds vs yesterday", prefix, mins, secs)
}
