# Heimdall
A Great Bridge Shall Open The Way

# Data Analytics Application

Heimdall is a modular, plugin-based data analytics application with clear separation of concerns. The design aligns with SOLID principles and enables both UI-based and headless operation modes.

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/Heimdall.git
cd Heimdall
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

4. If you want to use R integration features, make sure R is installed on your system, along with these packages:
```
R -e "install.packages(c('ggplot2'), repos='https://cloud.r-project.org')"
```

## Usage

### Running the GUI Application

```
python main.py
```

### Command Line Options

- `--config`: Path to a custom configuration file
- `--headless`: Run in headless mode (no UI)
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Example:
```
python main.py --log-level DEBUG
```

## Features

### Finance Domain
- **Stock Analysis**: Generate and visualize stock price data
- **Portfolio Allocation**: Analyze portfolio distribution with pie charts
- **CSV Export**: Export all generated data as CSV files

## Architecture Overview

The application follows a modular, plugin-based architecture with clear separation of concerns.

```
heimdall/
├── core/           # Core application components
├── infrastructure/ # Technical infrastructure
├── presentation/   # UI components
├── domain/         # Domain models and services
├── plugins/        # Domain-specific plugins
└── analysis/       # Data science specific modules
```

### Key Design Principles

- **SOLID Principles**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **Plugin Architecture**: Domain-specific functionality implemented as plugins
- **Event-Driven Communication**: Decoupled components communicating via events
- **Headless Operation**: All business logic operable without UI
- **Domain-Driven Design**: Business domains as organizational structure

### Core Components

- **Application Orchestrator**: Initializes and coordinates all system components
- **Event Bus**: Facilitates communication between decoupled components
- **Plugin Manager**: Manages the discovery, loading, and lifecycle of plugins
- **Configuration Manager**: Handles application configuration from multiple sources
- **Async Executor**: Provides asynchronous execution capabilities

### Infrastructure Layer

- **Database Integration**: Provides access to various database systems
- **R Integration**: Enables execution of R scripts from Python
- **Logging System**: Comprehensive logging infrastructure
- **Export System**: Manages data export to various formats

# Data Analytics Application Architecture Design Document

For a detailed architecture overview, see the [Architecture Design Document](docs/architecture.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.