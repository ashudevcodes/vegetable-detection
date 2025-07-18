package models

import "time"

type PriceData struct {
	Price       float64   `json:"price"`
	Unit        string    `json:"unit"`
	Location    string    `json:"location"`
	LastUpdated time.Time `json:"last_updated"`
}

type VegetablePrice struct {
	Vegetable string  `json:"vegetable"`
	Price     float64 `json:"price"`
	Unit      string  `json:"unit"`
	Location  string  `json:"location"`
}

type HealthResponse struct {
	Status  string `json:"status"`
	Message string `json:"message"`
	Time    string `json:"time"`
}

type PriceDatabase map[string]map[string]PriceData
