package handlers

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/gorilla/mux"
	"vegetable-price-detector/models"
)

type PriceHandler struct {
	db models.PriceDatabase
}

func NewPriceHandler() *PriceHandler {
	return &PriceHandler{
		db: initializePriceDB(),
	}
}

func (h *PriceHandler) GetPrice(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)

	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	vars := mux.Vars(r)
	vegetable := vars["vegetable"]
	location := r.URL.Query().Get("location")

	if location == "" {
		location = "Delhi"
	}

	// Get price from database
	if vegData, exists := h.db[vegetable]; exists {
		if priceData, locationExists := vegData[location]; locationExists {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(priceData)
			return
		}
	}

	// Default fallback price
	defaultPrice := models.PriceData{
		Price:       30,
		Unit:        "kg",
		Location:    location,
		LastUpdated: time.Now(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(defaultPrice)
}

func (h *PriceHandler) GetAllPrices(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)

	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	location := r.URL.Query().Get("location")
	if location == "" {
		location = "Delhi"
	}

	var prices []models.VegetablePrice

	for vegetable, locations := range h.db {
		if priceData, exists := locations[location]; exists {
			prices = append(prices, models.VegetablePrice{
				Vegetable: vegetable,
				Price:     priceData.Price,
				Unit:      priceData.Unit,
				Location:  priceData.Location,
			})
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(prices)
}

func (h *PriceHandler) Health(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)

	response := models.HealthResponse{
		Status:  "healthy",
		Message: "Go price service is running",
		Time:    time.Now().Format(time.RFC3339),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
}

func initializePriceDB() models.PriceDatabase {
	return models.PriceDatabase{
		"tomato": {
			"Delhi":     {Price: 25, Unit: "kg", Location: "Delhi", LastUpdated: time.Now()},
			"Mumbai":    {Price: 28, Unit: "kg", Location: "Mumbai", LastUpdated: time.Now()},
			"Bangalore": {Price: 26, Unit: "kg", Location: "Bangalore", LastUpdated: time.Now()},
			"Chennai":   {Price: 27, Unit: "kg", Location: "Chennai", LastUpdated: time.Now()},
			"Kolkata":   {Price: 24, Unit: "kg", Location: "Kolkata", LastUpdated: time.Now()},
			"Hyderabad": {Price: 26, Unit: "kg", Location: "Hyderabad", LastUpdated: time.Now()},
		},
		"onion": {
			"Delhi":     {Price: 42, Unit: "kg", Location: "Delhi", LastUpdated: time.Now()},
			"Mumbai":    {Price: 38, Unit: "kg", Location: "Mumbai", LastUpdated: time.Now()},
			"Bangalore": {Price: 40, Unit: "kg", Location: "Bangalore", LastUpdated: time.Now()},
			"Chennai":   {Price: 44, Unit: "kg", Location: "Chennai", LastUpdated: time.Now()},
			"Kolkata":   {Price: 36, Unit: "kg", Location: "Kolkata", LastUpdated: time.Now()},
			"Hyderabad": {Price: 41, Unit: "kg", Location: "Hyderabad", LastUpdated: time.Now()},
		},
		"potato": {
			"Delhi":     {Price: 35, Unit: "kg", Location: "Delhi", LastUpdated: time.Now()},
			"Mumbai":    {Price: 32, Unit: "kg", Location: "Mumbai", LastUpdated: time.Now()},
			"Bangalore": {Price: 33, Unit: "kg", Location: "Bangalore", LastUpdated: time.Now()},
			"Chennai":   {Price: 36, Unit: "kg", Location: "Chennai", LastUpdated: time.Now()},
			"Kolkata":   {Price: 30, Unit: "kg", Location: "Kolkata", LastUpdated: time.Now()},
			"Hyderabad": {Price: 34, Unit: "kg", Location: "Hyderabad", LastUpdated: time.Now()},
		},
		"carrot": {
			"Delhi":     {Price: 55, Unit: "kg", Location: "Delhi", LastUpdated: time.Now()},
			"Mumbai":    {Price: 52, Unit: "kg", Location: "Mumbai", LastUpdated: time.Now()},
			"Bangalore": {Price: 50, Unit: "kg", Location: "Bangalore", LastUpdated: time.Now()},
			"Chennai":   {Price: 58, Unit: "kg", Location: "Chennai", LastUpdated: time.Now()},
			"Kolkata":   {Price: 48, Unit: "kg", Location: "Kolkata", LastUpdated: time.Now()},
			"Hyderabad": {Price: 53, Unit: "kg", Location: "Hyderabad", LastUpdated: time.Now()},
		},
		"cauliflower": {
			"Delhi":     {Price: 30, Unit: "kg", Location: "Delhi", LastUpdated: time.Now()},
			"Mumbai":    {Price: 35, Unit: "kg", Location: "Mumbai", LastUpdated: time.Now()},
			"Bangalore": {Price: 32, Unit: "kg", Location: "Bangalore", LastUpdated: time.Now()},
			"Chennai":   {Price: 38, Unit: "kg", Location: "Chennai", LastUpdated: time.Now()},
			"Kolkata":   {Price: 28, Unit: "kg", Location: "Kolkata", LastUpdated: time.Now()},
			"Hyderabad": {Price: 31, Unit: "kg", Location: "Hyderabad", LastUpdated: time.Now()},
		},
	}
}
