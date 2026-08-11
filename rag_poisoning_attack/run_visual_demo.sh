#!/bin/bash
# Run the RAG Poisoning Attack Visual Demo (Streamlit)

echo "🗄️  Starting RAG Poisoning Attack Visual Demo..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing..."
    pip install streamlit
fi

# Check if Anthropic key is set
if [ -z "$ANTHROPIC_API_KEY" ] && [ ! -f "$(dirname "$0")/.env" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set and no .env file found"
    echo "   Claude mode will not work. Copy .env.example to .env and add your key."
    echo ""
fi

# Check if Ollama is running
if command -v ollama &> /dev/null; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is running"
    else
        echo "⚠️  Ollama not running. Start with: ollama serve"
    fi
else
    echo "ℹ️  Ollama not installed. Only Claude mode will work."
fi

echo ""
echo "🚀 Launching visual demo..."
echo "   URL: http://localhost:8501"
echo ""

# Run streamlit
cd "$(dirname "$0")"
streamlit run visual_demo_app.py
