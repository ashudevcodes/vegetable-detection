package models

import "time"

type PriceData struct {
	Price       float64   `json:"price"`
	Unit        string    `json:"unit"`
	Location    string    `json:"location"`
	LastUpdated time.Time `json:"last_updated"`
}

type PriceResponse struct {
	Vegetable   string    `json:"vegetable"`
	Price       float64   `json:"price"`
	Unit        string    `json:"unit"`
	Location    string    `json:"location"`
	LastUpdated time.Time `json:"last_updated"`
	Currency    string    `json:"currency"`
}

type VegetablePrice struct {
	Vegetable string  `json:"vegetable"`
	Price     float64 `json:"price"`
	Unit      string  `json:"unit"`
	Location  string  `json:"location"`
	Currency  string  `json:"currency"`
}

type MarketSummary struct {
	Location        string           `json:"location"`
	TotalVegetables int              `json:"total_vegetables"`
	AveragePrice    float64          `json:"average_price"`
	Currency        string           `json:"currency"`
	Unit            string           `json:"unit"`
	Vegetables      []VegetablePrice `json:"vegetables"`
	Timestamp       time.Time        `json:"timestamp"`
}

type VegetablesResponse struct {
	Vegetables []string `json:"vegetables"`
	Total      int      `json:"total"`
}

type LocationsResponse struct {
	Locations []string `json:"locations"`
	Default   string   `json:"default"`
	Total     int      `json:"total"`
}

type BatchPriceRequest struct {
	Vegetables []string `json:"vegetables"`
	Location   string   `json:"location"`
}

type HealthResponse struct {
	Status  string `json:"status"`
	Message string `json:"message"`
	Time    string `json:"time"`
	Service string `json:"service"`
}

type PriceDatabase map[string]map[string]PriceData
