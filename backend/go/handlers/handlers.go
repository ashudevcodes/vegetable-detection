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

type PriceEntry struct {
	Date   string `json:"date"`
	Tomato int    `json:"tomato"`
	Onion  int    `json:"onion"`
	Potato int    `json:"potato"`
}

var mockPriceHistory = []PriceEntry{
	{Date: "2025-07-13", Tomato: 30, Onion: 20, Potato: 25},
	{Date: "2025-07-14", Tomato: 32, Onion: 22, Potato: 26},
	{Date: "2025-07-15", Tomato: 31, Onion: 21, Potato: 24},
	{Date: "2025-07-16", Tomato: 33, Onion: 23, Potato: 27},
	{Date: "2025-07-17", Tomato: 34, Onion: 24, Potato: 28},
	{Date: "2025-07-18", Tomato: 35, Onion: 25, Potato: 29},
	{Date: "2025-07-19", Tomato: 36, Onion: 26, Potato: 30},
}

// GetPriceHistory handles GET /api/price-history
func (h *PriceHandler) GetPriceHistory(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	// Encode the whole slice
	println(mockPriceHistory)
	if err := json.NewEncoder(w).Encode(mockPriceHistory); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

// Get price for specific vegetable
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

	if vegData, exists := h.db[vegetable]; exists {
		if priceData, locationExists := vegData[location]; locationExists {
			response := models.PriceResponse{
				Vegetable:   vegetable,
				Price:       priceData.Price,
				Unit:        priceData.Unit,
				Location:    priceData.Location,
				LastUpdated: priceData.LastUpdated,
				Currency:    "INR",
			}
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(response)
			return
		}
	}

	// Default fallback price
	defaultPrice := models.PriceResponse{
		Vegetable:   vegetable,
		Price:       30,
		Unit:        "kg",
		Location:    location,
		LastUpdated: time.Now(),
		Currency:    "INR",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(defaultPrice)
}

// Get all prices for a location
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
				Currency:  "INR",
			})
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(prices)
}

// Get market summary
func (h *PriceHandler) GetMarketSummary(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	vars := mux.Vars(r)
	location := vars["location"]

	var prices []models.VegetablePrice
	totalPrice := 0.0
	count := 0

	for vegetable, locations := range h.db {
		if priceData, exists := locations[location]; exists {
			prices = append(prices, models.VegetablePrice{
				Vegetable: vegetable,
				Price:     priceData.Price,
				Unit:      priceData.Unit,
				Location:  priceData.Location,
				Currency:  "INR",
			})
			totalPrice += priceData.Price
			count++
		}
	}

	avgPrice := 0.0
	if count > 0 {
		avgPrice = totalPrice / float64(count)
	}

	summary := models.MarketSummary{
		Location:        location,
		TotalVegetables: count,
		AveragePrice:    avgPrice,
		Currency:        "INR",
		Unit:            "kg",
		Vegetables:      prices,
		Timestamp:       time.Now(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(summary)
}

// Get supported vegetables
func (h *PriceHandler) GetVegetables(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	var vegetables []string
	for veg := range h.db {
		vegetables = append(vegetables, veg)
	}

	response := models.VegetablesResponse{
		Vegetables: vegetables,
		Total:      len(vegetables),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Get supported locations
func (h *PriceHandler) GetLocations(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	locations := []string{"Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"}

	response := models.LocationsResponse{
		Locations: locations,
		Default:   "Delhi",
		Total:     len(locations),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Batch price lookup (for ML service)
func (h *PriceHandler) GetBatchPrices(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	var request models.BatchPriceRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	var response []models.PriceResponse
	for _, vegetable := range request.Vegetables {
		location := request.Location
		if location == "" {
			location = "Delhi"
		}

		if vegData, exists := h.db[vegetable]; exists {
			if priceData, locationExists := vegData[location]; locationExists {
				response = append(response, models.PriceResponse{
					Vegetable:   vegetable,
					Price:       priceData.Price,
					Unit:        priceData.Unit,
					Location:    priceData.Location,
					LastUpdated: priceData.LastUpdated,
					Currency:    "INR",
				})
				continue
			}
		}

		// Default fallback
		response = append(response, models.PriceResponse{
			Vegetable:   vegetable,
			Price:       30,
			Unit:        "kg",
			Location:    location,
			LastUpdated: time.Now(),
			Currency:    "INR",
		})
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func (h *PriceHandler) Health(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)

	response := models.HealthResponse{
		Status:  "healthy",
		Message: "Go pricing service is running",
		Time:    time.Now().Format(time.RFC3339),
		Service: "pricing",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
}

// ... your existing initializePriceDB function ...

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
