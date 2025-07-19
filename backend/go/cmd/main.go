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
	priceHandler := handlers.NewPriceHandler()

	r.HandleFunc("/api/price/{vegetable}", priceHandler.GetPrice).Methods("GET", "OPTIONS")
	r.HandleFunc("/api/prices", priceHandler.GetAllPrices).Methods("GET", "OPTIONS")
	r.HandleFunc("/api/vegetables", priceHandler.GetVegetables).Methods("GET", "OPTIONS")
	r.HandleFunc("/api/locations", priceHandler.GetLocations).Methods("GET", "OPTIONS")
	r.HandleFunc("/api/market-summary/{location}", priceHandler.GetMarketSummary).Methods("GET", "OPTIONS")
	r.HandleFunc("/api/batch-prices", priceHandler.GetBatchPrices).Methods("POST", "OPTIONS")
	r.HandleFunc("/health", priceHandler.Health).Methods("GET", "OPTIONS")

	// New route for the mock price history
	r.HandleFunc("/api/price-history", priceHandler.GetPriceHistory).Methods("GET", "OPTIONS")

	fmt.Println("Go Pricing Service running on :9000")
	log.Fatal(http.ListenAndServe(":9000", r))
}
