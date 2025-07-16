package main

import (
	"bytes"
	"encoding/json"
	"github.com/gin-gonic/gin"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
)

type Box struct {
	X      int    `json:"x"`
	Y      int    `json:"y"`
	Width  int    `json:"width"`
	Height int    `json:"height"`
	Label  string `json:"label"`
}

func main() {
	r := gin.Default()

	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		c.Next()
	})

	r.POST("/upload", func(c *gin.Context) {

		file, err := c.FormFile("image")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "file required"})
			return
		}

		path := filepath.Join("/tmp", file.Filename)
		c.SaveUploadedFile(file, path)

		buf := new(bytes.Buffer)
		writer := multipart.NewWriter(buf)
		f, _ := os.Open(path)
		defer f.Close()
		formFile, _ := writer.CreateFormFile("image", filepath.Base(path))
		io.Copy(formFile, f)
		writer.Close()

		resp, err := http.Post("http://detection:5000/detect", writer.FormDataContentType(), buf)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "detection service failed"})
			return
		}
		defer resp.Body.Close()

		var boxes []Box
		json.NewDecoder(resp.Body).Decode(&boxes)
		c.JSON(http.StatusOK, gin.H{"boxes": boxes})
	})

	r.Run(":8080")
}
