# EmoStream - Real Time Streaming of Emoji Bursts

A real-time emoji streaming application that processes emoji reactions through a complete data pipeline using Kafka, Spark, and Streamlit.

https://github.com/user-attachments/assets/e7ca82ea-038d-43a0-b6ab-a6b1edb3ab27


## Features

- **Real-time Emoji Processing**: Live streaming of emoji reactions with real-time aggregation
- **Distributed Architecture**: Uses Apache Kafka for message streaming and Spark for data processing
- **Interactive Visualization**: Streamlit-based dashboard for viewing emoji streams
- **Scalable Design**: Handles high-volume emoji bursts with windowed aggregation
- **Multi-client Support**: Supports multiple concurrent clients sending emoji data
- **Automated Pipeline**: Single-command startup with automated terminal management

## Architecture Components

- **Flask API Server** (`server.py`): REST API for receiving emoji data
- **Kafka Integration**: Message streaming between components
- **Spark Aggregation** (`spark_agg.py`): Real-time windowed processing of emoji streams
- **Streamlit App** (`app.py`): Interactive dashboard for emoji visualization
- **Load Testing** (`client_post_test.py`): Automated client for generating emoji traffic

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- UV package manager
- A GUI terminal (gnome-terminal, konsole, etc.) or tmux/screen

### Installation & Startup

Simply run the automated pipeline script:

```bash
./pipeline.sh
```

The script will:
1. Start Kafka and Zookeeper services via Docker Compose
2. Launch the Flask API server
3. Open separate terminals for:
   - Spark aggregation processing
   - Two client test instances (for load testing)
   - Streamlit dashboard

### Manual Startup (if preferred)

1. Start Kafka infrastructure:
   ```bash
   docker-compose up -d
   ```

2. Start the Flask API server:
   ```bash
   python server.py
   ```

3. Run Spark aggregation (in separate terminal):
   ```bash
   python spark_agg.py
   ```

4. Start the Streamlit app (in separate terminal):
   ```bash
   uv run python app.py
   ```

5. Run client tests (optional, in separate terminals):
   ```bash
   python client_post_test.py
   ```

## How It Works

1. **Data Ingestion**: Clients send emoji data to Flask API (`/api` endpoint)
2. **Message Streaming**: Flask publishes messages to Kafka topic `topic1`
3. **Real-time Processing**: Spark consumes from `topic1`, aggregates emoji counts in 2-second windows
4. **Output Stream**: Processed data is published to Kafka topic `topic2`
5. **Visualization**: Streamlit app consumes from `topic2` and displays emoji bursts




## Data Flow

```
Client  Flask API  Kafka (topic1)  Spark Aggregation  Kafka (topic2)  Streamlit Dashboard
```

