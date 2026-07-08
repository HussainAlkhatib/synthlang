package main

import (
    "net"
    "sync"
)

var (
    activeConnections int
    mu sync.Mutex
)

//export network_connect
func network_connect(address string) int {
    conn, err := net.Dial("tcp", address)
    if err != nil {
        return 0
    }
    mu.Lock()
    activeConnections++
    connNum := activeConnections
    mu.Unlock()
    conn.Close()
    return connNum
}

//export network_listen
func network_listen(address string) int {
    listener, err := net.Listen("tcp", address)
    if err != nil {
        return 0
    }
    _ = listener
    return 1
}

//export network_broadcast
func network_broadcast(message string, port int) {
    addr := &net.UDPAddr{IP: net.ParseIP("255.255.255.255"), Port: port}
    conn, _ := net.DialUDP("udp", nil, addr)
    if conn != nil {
        conn.Write([]byte(message))
    }
}

func main() {}