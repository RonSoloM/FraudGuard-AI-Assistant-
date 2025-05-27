"""
AI Model Integration Module

This module handles the integration with AI models for natural language processing
of questions that don't match predefined SQL queries.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from supported_questions import INTENTS

class MistralHandler:
    _instance = None
    _model = None
    _tokenizer = None
    _initialized = False

    def __new__(cls, model_name="microsoft/phi-2"):
        if cls._instance is None:
            cls._instance = super(MistralHandler, cls).__new__(cls)
            cls._instance.model_name = model_name
        return cls._instance

    def __init__(self, model_name="microsoft/phi-2"):
        """
        Initialize the AI model handler.
        
        Args:
            model_name (str): Name of the model to use
        """
        if not self._initialized:
            self.model_name = model_name
            self.initialize_model()
            self._initialized = True

    def initialize_model(self):
        """Initialize the model and tokenizer."""
        try:
            if self._tokenizer is None:
                print("Loading tokenizer...")
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                # Set padding token
                if self._tokenizer.pad_token is None:
                    self._tokenizer.pad_token = self._tokenizer.eos_token
            
            if self._model is None:
                print("Loading model...")
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    low_cpu_mem_usage=True,
                    use_cache=True  # Enable KV cache
                )
                # Set model's padding token
                self._model.config.pad_token_id = self._tokenizer.pad_token_id
                
                # Move model to GPU if available
                if torch.cuda.is_available():
                    self._model = self._model.cuda()
                    # Enable model optimization
                    self._model.eval()  # Set to evaluation mode
                    torch.cuda.empty_cache()  # Clear GPU cache
                print("Model loaded successfully!")
        except Exception as e:
            print(f"Error initializing AI model: {e}")

    def _create_context_prompt(self, question: str) -> str:
        """
        Create a context-aware prompt that includes information about supported questions and their SQL queries.
        
        Args:
            question (str): The user's question
            
        Returns:
            str: The context-aware prompt
        """
        # Create a context about supported questions and their SQL queries
        context = "I am a fraud analysis assistant. I know the following questions and their SQL queries:\n"
        
        for intent, data in INTENTS.items():
            context += f"\n- {intent.replace('_', ' ').title()}:\n"
            context += "  Examples:\n"
            for example in data["examples"]:
                context += f"    * {example}\n"
            context += "  SQL Query:\n"
            # Format the SQL query for better readability
            sql_lines = data["query"].split("\n")
            for line in sql_lines:
                context += f"    {line}\n"
        
        context += "\nIf the question matches any of these patterns, I should suggest using the corresponding SQL query. "
        context += "Otherwise, I should provide a brief fraud analysis response.\n\n"
        
        return f"{context}Q: {question}\nA:"

    def generate_response(self, question: str) -> str:
        """
        Generate a response using the AI model.
        
        Args:
            question (str): The user's question
            
        Returns:
            str: The model's response
        """
        if not self._model or not self._tokenizer:
            return "AI model is not initialized. Please check the model installation."

        try:
            # Create a context-aware prompt
            prompt = self._create_context_prompt(question)

            # Generate response with optimized parameters for speed
            with torch.no_grad():  # Disable gradient calculation
                inputs = self._tokenizer(
                    prompt,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=256,  # Reduced for faster processing
                    add_special_tokens=True
                )
                if torch.cuda.is_available():
                    inputs = inputs.to("cuda")
                    
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=64,       # Reduced for faster responses
                    temperature=0.3,         # Lower for more focused responses
                    do_sample=False,         # Disable sampling for faster generation
                    num_beams=1,             # Single beam for faster generation
                    pad_token_id=self._tokenizer.pad_token_id,
                    early_stopping=True,
                    repetition_penalty=1.2,   # Prevent repetitive responses
                    length_penalty=1.0,       # Neutral length penalty
                    no_repeat_ngram_size=3   # Prevent repetition of phrases
                )
            
            response = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the model's response (remove the prompt)
            response = response.split("A:")[-1].strip()
            
            # Post-process the response
            response = self._post_process_response(response)
            
            return response
        except Exception as e:
            print(f"Error in generate_response: {str(e)}")
            return f"Error generating response: {str(e)}"

    def _post_process_response(self, response: str) -> str:
        """Post-process the model's response to improve quality."""
        # Remove any remaining prompt artifacts
        response = response.replace("Q:", "").strip()
        
        # Ensure the response is not too long
        if len(response) > 150:  # Reduced for faster responses
            response = response[:147] + "..."
        
        # Add a period if the response doesn't end with punctuation
        if response and not response[-1] in ".!?":
            response += "."
            
        return response

    def is_available(self) -> bool:
        """Check if the model is available and initialized."""
        return self._model is not None and self._tokenizer is not None 