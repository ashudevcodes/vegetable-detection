package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"vegetable-price-detector/handlers"
)

func main() {
	r := mux.NewRouter()

	// Initialize handlers
	priceHandler := handlers.NewPriceHandler()

	// API routes
	r.HandleFunc("/api/prices/{vegetable}", priceHandler.GetPrice).Methods("GET", "OPTIONS")
	r.HandleFunc("/api/prices", priceHandler.GetAllPrices).Methods("GET", "OPTIONS")
	r.HandleFunc("/health", priceHandler.Health).Methods("GET", "OPTIONS")

	fmt.Println("Go Price Service running on :9000")
	log.Fatal(http.ListenAndServe(":9000", r))
}
