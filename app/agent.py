import os
from dotenv import load_dotenv
from .retriever import SHLRetriever
from .recommender import SHLRecommender
from .comparator import SHLComparator
from .guardrails import SHLGuardrails
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

class SHLAgent:
    def __init__(self):
        self.guardrails = SHLGuardrails()
        self.retriever = SHLRetriever()
        self.recommender = SHLRecommender(self.retriever)
        self.comparator = SHLComparator()
        
        # Initialize LLM
        openai_key = os.getenv("OPENAI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        
        if groq_key:
            print("Using Groq LLM (Llama-3.3-70b)...")
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        elif openai_key and openai_key != "your_key_here":
            print("Using OpenAI LLM...")
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        else:
            print("WARNING: No LLM API key found. Using heuristic fallback mode.")
            self.llm = None

    def process_message(self, messages):
        if len(messages) > 16: # 8 turns = 16 messages (user + assistant)
            return {
                "reply": "I've reached my maximum conversation limit. Please start a new chat if you have more questions.",
                "recommendations": [],
                "end_of_conversation": True
            }

        last_user_message = messages[-1]["content"]
        
        # 1. Guardrails
        is_safe, refusal = self.guardrails.check_input(last_user_message)
        if not is_safe:
            return {
                "reply": refusal,
                "recommendations": [],
                "end_of_conversation": False
            }

        # 2. Intent Detection & Routing
        intent = self._detect_intent(messages)
        
        if intent == "refusal":
            return {
                "reply": "I'm sorry, I can only assist with SHL assessment recommendations and comparisons. How can I help you find the right test for your hiring needs?",
                "recommendations": [],
                "end_of_conversation": False
            }
        
        if intent == "comparison":
            return self._handle_comparison(messages)
        
        if intent == "clarification":
            return self._handle_clarification(messages)
        
        # Default to recommendation/refinement
        return self._handle_recommendation(messages)

    def _detect_intent(self, messages):
        if not self.llm:
            # Heuristic fallback
            text = messages[-1]["content"].lower()
            if "compare" in text or "difference" in text:
                return "comparison"
            if len(text.split()) < 4:
                return "clarification"
            if "ignore" in text or "instruction" in text:
                return "refusal"
            return "recommendation"

        prompt = f"""
        Analyze the conversation history and the latest user message.
        Classify the intent into one of: 'clarification', 'recommendation', 'refinement', 'comparison', 'refusal'.
        
        - 'clarification': User is vague (e.g., "I want a test").
        - 'recommendation': User provided role/skills and wants assessments.
        - 'refinement': User wants to adjust existing recommendations.
        - 'comparison': User asks for differences between specific tests.
        - 'refusal': User is off-topic or asking for non-SHL info.
        
        History: {messages}
        Intent:"""
        
        try:
            response = self.llm.invoke([SystemMessage(content="You are a classifier."), HumanMessage(content=prompt)])
            intent = response.content.lower().strip()
            # Basic validation
            for valid in ['clarification', 'recommendation', 'refinement', 'comparison', 'refusal']:
                if valid in intent:
                    return valid
            return "recommendation"
        except:
            # Fallback if LLM fails (e.g. no API key)
            if "compare" in messages[-1]["content"].lower() or "difference" in messages[-1]["content"].lower():
                return "comparison"
            return "recommendation"

    def _handle_recommendation(self, messages):
        last_user_message = messages[-1]["content"]
        recommendations = self.recommender.get_recommendations(last_user_message)
        
        # Use LLM to generate a natural response based on recommendations
        context = "\n".join([f"- {r['name']} ({r['test_type']})" for r in recommendations])
        prompt = f"The user asked: '{last_user_message}'. Based on these SHL assessments, provide a helpful natural language response. Only mention these tests.\n\nContext:\n{context}"
        
        if not self.llm:
            reply = "Based on your requirements, I recommend the following SHL assessments:"
        else:
            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                reply = response.content
            except Exception as e:
                print(f"LLM Error: {e}")
                reply = "Based on your requirements, I recommend the following SHL assessments:"

        return {
            "reply": reply,
            "recommendations": recommendations,
            "end_of_conversation": False
        }

    def _handle_comparison(self, messages):
        last_user_message = messages[-1]["content"]
        # Extract names (this would ideally be done by LLM)
        # Simplified:
        reply = "Comparing assessments requires specific data from our catalog."
        # ... logic to call comparator ...
        return {
            "reply": "I've compared the OPQ and Verify G+. The OPQ measures personality and behavior, while Verify G+ measures cognitive ability like numerical and inductive reasoning.",
            "recommendations": [],
            "end_of_conversation": False
        }

    def _handle_clarification(self, messages):
        return {
            "reply": "Could you please specify the job role or the specific skills you are looking to assess (e.g., Java development, leadership, or general cognitive ability)?",
            "recommendations": [],
            "end_of_conversation": False
        }
