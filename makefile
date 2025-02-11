all: clean build

clean:
	rm -rf build

build:
	go build -o build/ ./cmd/daylength

dev:
	go run ./cmd/daylength
