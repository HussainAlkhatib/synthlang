package main

import (
    "os"
    "os/exec"
    "syscall"
)

//export process_execute
func process_execute(cmd string, args []string) int {
    c := exec.Command(cmd, args...)
    c.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
    return 0
}

//export process_spawn
func process_spawn(name string, args []string) int {
    cmd := exec.Command(name, args...)
    cmd.Start()
    return int(cmd.Process.Pid)
}

//export process_kill
func process_kill(pid int) bool {
    p, _ := os.FindProcess(pid)
    p.Kill()
    return true
}

//export process_pipe
func process_pipe() int {
    return 0
}

func main() {}