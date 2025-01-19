# Using `screen` on Ubuntu Command Line

## 1. Start a New Screen Session
To create a new named screen session:
```bash
screen -S session_name
```
Replace `session_name` with a meaningful name for your session.

---

## 2. Detach from the Current Session
To detach from the session (keep it running in the background), press:
```
Ctrl + A, then D
```

---

## 3. List All Active Sessions
To view all running screen sessions, type:
```bash
screen -ls
```

---

## 4. Reattach to an Existing Session
- To reattach to a specific session:
  ```bash
  screen -r session_name
  ```
  Replace `session_name` with the name of the session you want to reattach to.

- If there is only one session, you can simply use:
  ```bash
  screen -r
  ```

---

## 5. Exit a Screen Session
- Inside a session, type `exit` to terminate it:
  ```bash
  exit
  ```

- If you have a running process and want to close the screen session while leaving the process running, detach first using `Ctrl + A, D`.

---

## 6. Kill a Screen Session
If needed, you can kill a specific session:
```bash
screen -X -S session_name quit
```
Replace `session_name` with the name of the session you want to kill.

---

## 7. Shortcut Recap
- **Start a session**: `screen -S session_name`
- **Detach**: `Ctrl + A, D`
- **List sessions**: `screen -ls`
- **Reattach**: `screen -r session_name`
- **Exit session**: `exit`
- **Kill session**: `screen -X -S session_name quit`

---

## Notes
- Use `screen` to run long-term tasks, especially when disconnecting from SSH. The process continues running even if you log out of your terminal session.

