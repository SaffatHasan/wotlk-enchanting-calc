# Supports hot reload
run:
	gin

# install deps and gin
setup:
	go mod tidy
	go get github.com/codegangsta/gin
