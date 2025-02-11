all: clean build

clean:
	rm -rf build

build:
	go build -o build/ ./cmd/daylight

dev:
	go run ./cmd/daylight
