all: clean build

clean:
	rm -rf build

build:
	go build -ldflags="-w -s" -o build/ ./cmd/daylight

dev:
	go run ./cmd/daylight
