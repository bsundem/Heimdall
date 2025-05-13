# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Heimdall is a data analytics application with a modular, plugin-based architecture following SOLID principles. The application is designed to support both UI-based and headless operation modes.

## Architecture

The application follows a carefully designed architecture with the following components:

### Core Components
- **Application Orchestrator**: Coordinates system components, handles configuration loading, plugin discovery, and lifecycle management
- **Event Bus**: Enables communication between decoupled components using publish-subscribe pattern
- **Plugin Manager**: Manages plugin discovery, loading, and lifecycle
- **Configuration Manager**: Handles application configuration from multiple sources
- **Async Executor**: Provides asynchronous execution capabilities

### Layers
- **Core**: Core application components
- **Infrastructure**: Technical infrastructure including database integration, R integration, logging, and export systems
- **Presentation**: UI components using PySide6 (Qt) framework
- **Domain**: Domain models and services
- **Plugins**: Domain-specific plugins
- **Analysis**: Data science specific modules

### Design Principles
- SOLID principles implementation
- Plugin architecture for domain-specific functionality
- Event-driven communication
- Headless operation capabilities
- Domain-driven design

## Data Flow Architecture
- Command processing flow
- Query processing flow
- Data analysis flow
- Export flow

## Technology Stack
- Python as primary language
- PySide6 for UI (Qt-based)
- SQLAlchemy for database access
- rpy2 for R integration
- asyncio for asynchronous operations
- pluggy for plugin management

## Project Structure
```
data_analytics_app/
├── core/           # Core application components
├── infrastructure/ # Technical infrastructure
├── presentation/   # UI components
├── domain/         # Domain models and services
├── plugins/        # Domain-specific plugins
└── analysis/       # Data science specific modules
```

Data science components follow Cookiecutter Data Science conventions:
```
analysis/
├── data/
│   ├── raw/                # Original, immutable data
│   ├── interim/            # Intermediate processed data
│   ├── processed/          # Final, canonical datasets
│   └── external/           # Data from third-party sources
│
├── models/                 # Trained and serialized models
├── notebooks/              # Jupyter notebooks for exploration
├── pipelines/              # Data processing pipelines
├── visualizations/         # Generated graphics and figures
└── scripts/                # Standalone analysis scripts
```

## Development Conventions
- Python package structure following domain boundaries
- Clear separation between interfaces and implementations
- Snake_case naming conventions as per Python standards
- Hierarchical loggers following package structure
- Domain-specific exception types
- Plugin hooks for domain-specific functionality

## Cross-Cutting Concerns
- Error handling with structured error hierarchy
- Security with authentication and authorization
- Comprehensive testing (unit, integration, end-to-end)
- Packaging and deployment using Conda and CI/CD
