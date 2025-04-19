package main

import (
    "encoding/json"
    "fmt"
    "math"
    "net/http"
    "strings"
    "time"
    "strconv"

    "github.com/google/uuid"
    "github.com/gorilla/mux"
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"
)


type ReceiptTable struct {
    ID   string          `gorm:"primaryKey" json:"id"`
    Data json.RawMessage `gorm:"type:json" json:"data"`
}

var db *gorm.DB

func initDB() {
    db, _ = gorm.Open(sqlite.Open("receipts.db"), &gorm.Config{})
    db.AutoMigrate(&ReceiptTable{})
}

func processReceiptHandler(w http.ResponseWriter, r *http.Request) {
    var receipt map[string]interface{}
    json.NewDecoder(r.Body).Decode(&receipt)


    id := uuid.New().String()

    receiptJSON, _ := json.Marshal(receipt)
    db.Create(&ReceiptTable{
        ID:   id,
        Data: receiptJSON,
    })

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{"id": id})
}

func getPointsHandler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id := vars["id"]

    var record ReceiptTable
    result := db.First(&record, "id = ?", id)
    if result.Error != nil {
        http.Error(w, "Receipt not found", http.StatusNotFound)
        return
    }

    var receipt map[string]interface{}
    json.Unmarshal(record.Data, &receipt)

    points := calculatePoints(receipt)

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]int{"points": points})
}

func calculatePoints(receipt map[string]interface{}) int {
    points := 0

    // Task 1
    retailer := receipt["retailer"].(string)
    for _, c := range retailer {
        if isAlphaNum(c) {
            points++
        }
    }

    // Task 2
    total := receipt["total"].(string)
    parts := strings.Split(total, ".")
    cents := parts[1]

    if cents == "00" {
        points += 50
    }

    // Task 3
    if cents == "25" || cents == "50" || cents == "75" || cents == "00" {
        points += 25
    }

    // Task 4
    items := receipt["items"].([]interface{})
    points += 5 * (len(items) / 2)

    // Task 5
    for _, item := range items {
        products := item.(map[string]interface{})
        desc := strings.TrimSpace(products["shortDescription"].(string))
        price, _ := strconv.ParseFloat(products["price"].(string), 64)
        if len(desc)%3 == 0 {
            points += int(math.Ceil(price * 0.2))
        }
    }

    // Task 6
    purchaseDate := receipt["purchaseDate"].(string)
    date, _ := time.Parse("2006-01-02", purchaseDate)
    if date.Day()%2 == 1 {
        points += 6
    }

    // Task 7
    purchaseTime := receipt["purchaseTime"].(string)
    t, _ := time.Parse("15:04", purchaseTime)
    if (t.Hour() == 14 && t.Minute() > 0) || (t.Hour() == 15) {
        points += 10
    }

    return points
}

func isAlphaNum(r rune) bool {
    return (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9')
}


func main() {
    initDB()

    r := mux.NewRouter()
    r.HandleFunc("/receipts/process", processReceiptHandler).Methods("POST")
    r.HandleFunc("/receipts/{id}/points", getPointsHandler).Methods("GET")

    fmt.Println("Server running at http://localhost:5000")
    http.ListenAndServe(":5000", r)
}
