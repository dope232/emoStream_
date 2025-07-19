#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-docker-compose.yml}"
SERVER_SCRIPT="${SERVER_SCRIPT:-server.py}"
SPARK_SCRIPT="${SPARK_SCRIPT:-spark_agg.py}"
CLIENT_SCRIPT="${CLIENT_SCRIPT:-client_post_test.py}"
APP_SCRIPT="${APP_SCRIPT:-app.py}"
DOCKER_HEALTH_TIMEOUT="${DOCKER_HEALTH_TIMEOUT:-60}"
SERVER_STARTUP_DELAY="${SERVER_STARTUP_DELAY:-5}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

cleanup() {
    log "Cleaning up processes..."
    if [[ -n "$DOCKER_COMPOSE_PID" ]]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

wait_for_docker() {
    log "Starting Docker Compose..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    log "Waiting for Docker services to be healthy..."
    local timeout=$DOCKER_HEALTH_TIMEOUT
    while [[ $timeout -gt 0 ]]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up.*healthy\|Up.*running"; then
            log "Docker services are ready"
            return 0
        fi
        sleep 2
        ((timeout-=2))
        log "Waiting for services... (${timeout}s remaining)"
    done
    
    log "ERROR: Docker services failed to start within ${DOCKER_HEALTH_TIMEOUT}s"
    exit 1
}

detect_terminal() {
    if [[ -n "$DISPLAY" ]] || [[ -n "$WAYLAND_DISPLAY" ]]; then
        if command -v gnome-terminal >/dev/null; then
            echo "gnome-terminal"
        elif command -v konsole >/dev/null; then
            echo "konsole"
        elif command -v xfce4-terminal >/dev/null; then
            echo "xfce4-terminal"
        elif command -v mate-terminal >/dev/null; then
            echo "mate-terminal"
        elif command -v terminator >/dev/null; then
            echo "terminator"
        elif command -v alacritty >/dev/null; then
            echo "alacritty"
        elif command -v kitty >/dev/null; then
            echo "kitty"
        elif command -v xterm >/dev/null; then
            echo "xterm"
        else
            echo "none"
        fi
    else
        echo "none"
    fi
}

spawn_terminal() {
    local title="$1"
    local command="$2"
    local terminal=$(detect_terminal)
    
    case "$terminal" in
        "gnome-terminal")
            gnome-terminal --title="$title" -- bash -c "$command; exec bash" &
            ;;
        "konsole")
            konsole --title "$title" -e bash -c "$command; exec bash" &
            ;;
        "xfce4-terminal")
            xfce4-terminal --title="$title" -e "bash -c '$command; exec bash'" &
            ;;
        "mate-terminal")
            mate-terminal --title="$title" -e "bash -c '$command; exec bash'" &
            ;;
        "terminator")
            terminator --title="$title" -e "bash -c '$command; exec bash'" &
            ;;
        "alacritty")
            alacritty -t "$title" -e bash -c "$command; exec bash" &
            ;;
        "kitty")
            kitty --title="$title" bash -c "$command; exec bash" &
            ;;
        "xterm")
            xterm -T "$title" -e bash -c "$command; exec bash" &
            ;;
        "none")
            if command -v tmux >/dev/null; then
                log "Using tmux session for $title"
                tmux new-session -d -s "$title" "$command"
            elif command -v screen >/dev/null; then
                log "Using screen session for $title"
                screen -dmS "$title" bash -c "$command"
            else
                log "WARNING: No GUI terminal or multiplexer found. Running $title in background..."
                bash -c "$command" &
            fi
            ;;
    esac
}

check_dependencies() {
    local missing_deps=()
    
    if ! command -v docker >/dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v docker-compose >/dev/null && ! command -v docker >/dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command -v python >/dev/null && ! command -v python3 >/dev/null; then
        missing_deps+=("python")
    fi
    
    if ! command -v uv >/dev/null; then
        missing_deps+=("uv")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log "ERROR: Missing dependencies: ${missing_deps[*]}"
        log "Please install missing dependencies and try again"
        exit 1
    fi
}

main() {
    log "Starting EmoStream Pipeline..."
    
    check_dependencies
    
    wait_for_docker
    
    log "Starting server.py..."
    python "$SERVER_SCRIPT" &
    SERVER_PID=$!
    sleep $SERVER_STARTUP_DELAY
    
    log "Spawning Spark aggregation terminal..."
    spawn_terminal "Spark-Aggregation" "python $SPARK_SCRIPT"
    
    log "Spawning client test terminals..."
    spawn_terminal "Client-Test-1" "python $CLIENT_SCRIPT"
    spawn_terminal "Client-Test-2" "python $CLIENT_SCRIPT"
    
    log "Starting app.py with uv..."
    spawn_terminal "EmoStream-App" "uv run python $APP_SCRIPT"
    
    log "Pipeline started successfully!"
    log "Press Ctrl+C to stop all services"
    
    if [[ $(detect_terminal) == "none" ]]; then
        log "TIP: Use 'tmux list-sessions' or 'screen -ls' to see running sessions"
    fi
    
    wait $SERVER_PID
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi