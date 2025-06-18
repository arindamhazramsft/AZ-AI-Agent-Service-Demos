# Azure AI Agent Service Demos

A comprehensive collection of Python-based demo applications showcasing various Azure AI technologies and frameworks. This repository demonstrates practical implementations of AI Agents, Azure AI Agent Service, Semantic Kernel, AutoGen, Model Router, Connected Agents, and Model Control Protocol (MCP).

## 🎯 Overview

This repository contains hands-on examples for developers looking to explore and implement Azure AI services in their applications. Each demo focuses on specific Azure AI capabilities and provides both console and UI-based implementations where applicable.

## 📁 Repository Structure

```
├── ai-agent/                     # Azure AI Agent Service demos
│   ├── ai-agent-bing-search.py   # Console demo with Bing search integration
│   ├── ai-agent-bing-search-ui.py # Streamlit UI for Bing search agent
│   ├── ai-agent-rag.py           # Console demo with RAG capabilities
│   ├── ai-agent-rag-ui.py        # Streamlit UI for RAG agent
│   ├── requirements.txt          # Dependencies
│   └── ContosoUniversityFAQ.pdf  # Sample document for RAG demos
│
├── sk/                           # Semantic Kernel demos
│   ├── ai-agent-sk.py            # Console demo using Semantic Kernel
│   ├── ai-agent-sk-ui.py         # Streamlit UI for SK agent
│   ├── multi-agent-lesson-planner-sk.py     # Multi-agent lesson planning
│   ├── multi-agent-lesson-planner-sk-ui.py  # UI for lesson planner
│   └── requirements.txt          # Dependencies
│
├── autogen/                      # AutoGen framework demos
│   ├── multi-agent-lesson-planner-autogen.py    # Console multi-agent demo
│   ├── multi-agent-lesson-planner-autogen-ui.py # UI multi-agent demo
│   └── requirements.txt          # Dependencies
│
├── model-router/                 # Azure OpenAI Model Router demos
│   ├── main.py                   # Model routing implementation
│   ├── questions.txt             # Sample questions for testing
│   ├── requirements.txt          # Dependencies
│   └── Model-Router.png          # Architecture diagram
│
├── connected-agents/             # Connected Agents demos
│   ├── main.py                   # Agent orchestration demo
│   ├── questions.txt             # Sample questions
│   ├── requirements.txt          # Dependencies
│   └── ContosoUniversityFAQ.pdf  # Sample document
│
└── mcp/                         # Model Control Protocol demos
    ├── mcp-client.py            # MCP client implementation
    ├── calculator-server.py     # Sample calculator server
    ├── bmi-calculator-server.py # BMI calculator server
    ├── requirements.txt         # Dependencies
    └── prep.txt                 # Setup instructions
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Azure Subscription** with appropriate AI services enabled
- **Azure CLI** (recommended for authentication)
- **Git** for cloning the repository

### Required Azure Resources

1. **Azure OpenAI Service** with deployed models
2. **Azure AI Agent Service** (preview)
3. **Bing Search API** (for search-enabled demos)
4. **Azure AI Studio Project** (for some demos)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd AZ-AI-Agent-Service-Demos
   ```

2. **Set up environment variables:**
   
   Create a `.env` file in each demo folder with the following variables:
   ```env
   # Azure OpenAI Configuration
   AOAI_API_KEY=your_openai_api_key
   AOAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
   MODEL_DEPLOYMENT_NAME=your_model_deployment_name
   MODEL_API_VERSION=2024-08-01-preview
   
   # Azure AI Project Configuration
   PROJECT_CONNECTION_STRING=your_project_connection_string
   AZURE_AI_PROJECT_ENDPOINT=your_project_endpoint
   
   # Bing Search Configuration
   BING_CONNECTION_NAME=your_bing_connection_name
   
   # Connected Agents Configuration
   ORCHESTRATOR_AGENT_ID=your_orchestrator_agent_id
   
   # Model Router Configuration
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_KEY=your_key
   ```

3. **Install dependencies for each demo:**
   ```bash
   # For AI Agent demos
   cd ai-agent
   pip install -r requirements.txt
   
   # For Semantic Kernel demos
   cd ../sk
   pip install -r requirements.txt
   
   # For AutoGen demos
   cd ../autogen
   pip install -r requirements.txt
   
   # For Model Router demos
   cd ../model-router
   pip install -r requirements.txt
   
   # For Connected Agents demos
   cd ../connected-agents
   pip install -r requirements.txt
   
   # For MCP demos
   cd ../mcp
   pip install -r requirements.txt
   ```

## 📖 Demo Descriptions

### 🤖 AI Agent Service Demos (`ai-agent/`)

**Bing Search Agent:**
- Demonstrates Azure AI Agent with Bing search capabilities
- Answers education-related questions using web search
- Available in both console and Streamlit UI versions

**RAG Agent:**
- Shows Retrieval Augmented Generation using file search
- Processes PDF documents for question answering
- Includes document upload and query functionality

### 🧠 Semantic Kernel Demos (`sk/`)

**Basic AI Agent:**
- Simple chat completion agent using Semantic Kernel
- Educational planning assistant functionality
- Demonstrates async programming patterns

**Multi-Agent Lesson Planner:**
- Collaborative agents for educational content creation
- Course planning and curriculum development
- Shows agent coordination capabilities

### 🔄 AutoGen Demos (`autogen/`)

**Multi-Agent Lesson Planner:**
- Round-robin group chat with multiple specialized agents
- Subject Expert, Curriculum Designer, and Assessment Specialist roles
- Demonstrates complex multi-agent workflows

### 🔀 Model Router Demo (`model-router/`)

**Intelligent Model Routing:**
- Routes requests to appropriate models based on content
- Demonstrates cost optimization and performance tuning
- Includes real-time model selection logic

### 🔗 Connected Agents Demo (`connected-agents/`)

**Agent Orchestration:**
- Shows how agents can work together in complex workflows
- Demonstrates thread management and message passing
- Includes agent flow visualization

### 🛠 Model Control Protocol (MCP) Demos (`mcp/`)

**Calculator Server:**
- Basic MCP server implementation
- Tool registration and execution
- Client-server communication patterns

## 🎮 Running the Demos

### Console Applications

Navigate to any demo folder and run the Python file:

```bash
# AI Agent Bing Search
cd ai-agent
python ai-agent-bing-search.py

# Semantic Kernel Agent
cd sk
python ai-agent-sk.py

# AutoGen Multi-Agent
cd autogen
python multi-agent-lesson-planner-autogen.py

# MCP Client
cd mcp
python mcp-client.py
```

### Streamlit UI Applications

For demos with UI components:

```bash
# AI Agent with UI
cd ai-agent
streamlit run ai-agent-bing-search-ui.py

# Model Router UI
cd model-router
streamlit run main.py

# Connected Agents UI
cd connected-agents
streamlit run main.py
```

The Streamlit apps will open in your default web browser at `http://localhost:8501`.

## 🧪 Testing the Demos

### Sample Test Scenarios

1. **Education Questions for Bing Search Agent:**
   - "What are the latest trends in online education?"
   - "How can AI improve student learning outcomes?"
   - "What are effective teaching strategies for STEM subjects?"

2. **RAG Agent with University FAQ:**
   - Upload the provided ContosoUniversityFAQ.pdf
   - Ask: "What are the admission requirements?"
   - Ask: "What financial aid options are available?"

3. **Lesson Planning Agents:**
   - Topic: "Introduction to Machine Learning"
   - Topic: "Photosynthesis in Biology"
   - Topic: "World War II History"

4. **Model Router Testing:**
   - Simple questions (routed to faster models)
   - Complex analytical tasks (routed to advanced models)
   - Creative writing requests (routed to creative models)

### Expected Outputs

- **Console demos:** Text-based responses with agent reasoning
- **UI demos:** Interactive interfaces with real-time responses
- **Multi-agent demos:** Collaborative conversations between agents
- **MCP demos:** Tool execution results and server responses

## 🔧 Configuration Tips

### Authentication

The demos support multiple authentication methods:

1. **Default Azure Credential** (recommended for development)
2. **Service Principal** (for production)
3. **Managed Identity** (for Azure-hosted applications)

### Model Selection

- **GPT-4:** Best for complex reasoning and analysis
- **GPT-3.5-Turbo:** Good balance of speed and capability
- **GPT-4-Turbo:** Optimized for longer contexts

### Performance Optimization

- Use async patterns for better responsiveness
- Implement caching for frequently accessed data
- Monitor token usage for cost optimization

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors:**
   - Verify environment variables are set correctly
   - Check Azure CLI login status: `az account show`
   - Ensure proper permissions on Azure resources

2. **Model Deployment Issues:**
   - Confirm model deployment names match configuration
   - Check model availability in your region
   - Verify API version compatibility

3. **Connection Problems:**
   - Test network connectivity to Azure endpoints
   - Check firewall and proxy settings
   - Verify service health in Azure Portal

4. **Package Dependencies:**
   - Use virtual environments to avoid conflicts
   - Update packages if compatibility issues arise
   - Check Python version compatibility

### Debug Tips

- Enable logging for detailed error information
- Use Azure Portal to monitor resource usage
- Check agent run status in Azure AI Studio
- Validate JSON responses for malformed data

## 📚 Additional Resources

- [Azure AI Agent Service Documentation](https://docs.microsoft.com/azure/ai-services/agents/)
- [Semantic Kernel Documentation](https://learn.microsoft.com/semantic-kernel/)
- [AutoGen Framework](https://github.com/microsoft/autogen)
- [Azure OpenAI Service](https://docs.microsoft.com/azure/ai-services/openai/)
- [Model Control Protocol](https://modelcontextprotocol.io/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests to improve these demos.

## 📄 License

This project is provided as sample code for educational and demonstration purposes. Please review and comply with Azure service terms and conditions.

## 🔗 Related Projects

- [Azure AI Samples](https://github.com/Azure-Samples/azure-ai-samples)
- [Semantic Kernel Samples](https://github.com/microsoft/semantic-kernel)
- [AutoGen Examples](https://github.com/microsoft/autogen/tree/main/python/packages/autogen-agentchat/examples)

---

**Note:** These demos are designed for learning and experimentation. For production use, please follow Azure security best practices and implement appropriate error handling, logging, and monitoring.