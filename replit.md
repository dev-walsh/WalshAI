# DeepSeek AI Telegram Bot

## Overview

This is a Telegram chatbot application that integrates with DeepSeek's AI API to provide conversational AI capabilities. The bot maintains conversation history, implements rate limiting, and provides a cost-effective alternative for AI-powered chat interactions through Telegram.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular Python architecture with clear separation of concerns:

- **Entry Point**: `main.py` serves as the application entry point and orchestrates the bot setup
- **Configuration Management**: `config.py` handles all environment variables and settings
- **Bot Logic**: `bot_handlers.py` contains all Telegram bot command and message handlers
- **External API Integration**: `deepseek_client.py` manages communication with the DeepSeek AI API

The architecture is designed for simplicity and maintainability, using a procedural approach with class-based organization for related functionality.

## Key Components

### Configuration System
- Environment variable-based configuration with `.env` file support
- Centralized settings for API keys, rate limits, timeouts, and message constraints
- Built-in validation for required configuration parameters

### Telegram Bot Integration
- Built on `python-telegram-bot` library for async Telegram API interactions
- Command handlers for `/start`, `/help`, and `/clear` commands
- Message handler for processing user text input
- Error handling and logging throughout the application

### AI Integration
- Custom DeepSeek API client with retry logic and session management
- Support for conversation context and message history
- Configurable model parameters (temperature, max tokens)

### Rate Limiting & Security
- Per-user rate limiting using sliding window approach
- Secure API key management through environment variables
- Request timeout and retry mechanisms

### Data Management
- In-memory conversation history storage per user
- Configurable conversation history limits
- No persistent database - conversation state is ephemeral

## Data Flow

1. **User Input**: User sends message to Telegram bot
2. **Rate Limiting**: System checks if user has exceeded rate limits
3. **Context Building**: Bot retrieves conversation history for the user
4. **AI Processing**: Message and context sent to DeepSeek API
5. **Response Handling**: AI response processed and sent back to user
6. **History Update**: Conversation history updated with user message and AI response

The system maintains conversation context by storing the last N messages per user in memory, allowing for contextual responses while managing memory usage.

## External Dependencies

### Core Dependencies
- `python-telegram-bot`: Telegram Bot API integration
- `requests`: HTTP client for DeepSeek API calls
- `python-dotenv`: Environment variable management

### External Services
- **Telegram Bot API**: For receiving and sending messages
- **DeepSeek AI API**: For generating AI responses
- **File System**: For logging (bot.log file)

### API Requirements
- Telegram Bot Token from @BotFather
- DeepSeek API Key from DeepSeek Platform

## Deployment Strategy

The application is designed for simple deployment with minimal infrastructure requirements:

### Environment Setup
- Python 3.8+ runtime environment
- Environment variables for API keys and configuration
- No database setup required (uses in-memory storage)

### Configuration
- All settings configurable through environment variables
- Default values provided for non-sensitive settings
- Support for `.env` file for local development

### Scalability Considerations
- Single-instance deployment (conversation history stored in memory)
- Rate limiting implemented per instance
- Stateless design allows for easy horizontal scaling with external session storage

### Monitoring & Logging
- Comprehensive logging to both file and console
- Error handling with detailed logging for debugging
- Request/response logging for API interactions

The deployment strategy prioritizes simplicity and cost-effectiveness, making it suitable for personal projects or small-scale deployments without requiring complex infrastructure.