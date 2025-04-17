package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
)

func homeHandler(w http.ResponseWriter, r *http.Request) {
    response := map[string]string{"message": "Hello, Go!"}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func greetHandler(w http.ResponseWriter, r *http.Request) {
    name := r.URL.Query().Get("name")
    if name == "" {
        name = "there"
    }
    response := map[string]string{"message": fmt.Sprintf("Hello, %s!", name)}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func main() {
    http.HandleFunc("/", homeHandler)
    http.HandleFunc("/api/greet", greetHandler)

    fmt.Println("Server starting at http://localhost:8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
