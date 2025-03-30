# ai_module/chatbot.py
from .ingredient_matcher import suggest_recipes_by_ingredients # Use a leading dot '.'
import re # For simple rule-based matching

# --- Very Simple Rule-Based Example ---
# A real chatbot would use Rasa, Dialogflow, or an LLM API

# Store minimal conversation state (in memory for this example)
conversation_state = {} 

def handle_chat_message(user_id: str, message: str) -> str:
    """Handles a user message and returns a chatbot response."""
    message_lower = message.lower()
    
    # Initialize state for new user
    if user_id not in conversation_state:
        conversation_state[user_id] = {}

    # Example Rule 1: User lists ingredients
    match_ingredients = re.search(r'(?:make|cook|prepare).*with\s+(.+)', message_lower)
    if match_ingredients:
        ingredients_text = match_ingredients.group(1)
        # Simple split, needs better parsing in reality
        ingredients = [ing.strip() for ing in ingredients_text.split(', ')] 
        if ' and ' in ingredients[-1]: # Handle "x, y and z"
             last_two = ingredients[-1].split(' and ')
             ingredients = ingredients[:-1] + last_two
        
        suggested_recipes = suggest_recipes_by_ingredients(ingredients, max_suggestions=3)
        if suggested_recipes:
            response = "Okay, with " + ", ".join(ingredients) + " I suggest:\n"
            for i, recipe in enumerate(suggested_recipes):
                response += f"{i+1}. {recipe['recipe_name']} (Missing {recipe['missing_count']} ingredients)\n"
            return response
        else:
            return f"Sorry, I couldn't find any recipes matching {', '.join(ingredients)} well."

    # Example Rule 2: User asks for something specific (e.g., quick)
    if "quick" in message_lower or "fast" in message_lower:
         # Here you would query recipes tagged as 'quick' or with short prep/cook times
         # Placeholder response:
         return "You want something quick? How about trying a stir-fry or a quick pasta dish?"

    # Example Rule 3: Simple greeting
    if message_lower in ["hi", "hello", "hey"]:
        return "Hello! How can I help you find a recipe today? You can tell me ingredients you have, or what you're craving."
        
    # Default response
    return "Sorry, I didn't quite understand that. You can tell me ingredients you have (e.g., 'What can I make with chicken, rice, and broccoli?') or what kind of meal you'd like."

# Remember to clear or manage conversation_state appropriately in a real app