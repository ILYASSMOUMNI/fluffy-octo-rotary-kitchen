# ai_module/services/chatbot.py
import logging
import os
from django.conf import settings

# --- Import the Google Generative AI library ---
try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
    google_ai_available = True
except ImportError:
    # ... (error handling for missing library) ...
    genai = None
    google_exceptions = None
    google_ai_available = False
    logging.warning("Google Generative AI library not found...")

logger = logging.getLogger(__name__)

# --- Configure Google AI Client and Model ---
gemini_model = None
if google_ai_available:
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        logger.error("GOOGLE_API_KEY not found in Django settings...")
    else:
        try:
            genai.configure(api_key=api_key)
            model_name = 'gemini-1.5-flash' # Or your preferred vision/text model

            # --- MODIFIED SYSTEM INSTRUCTIONS ---
            system_instruction_text = (
                "You are 'ChefBot', a friendly and knowledgeable recipe assistant for the 'RecipeApp'.\n"
                "Your primary function is to help users with recipe suggestions, ingredient usage, substitutions, and basic cooking questions.\n"
                "Keep your responses focused on food, recipes, and cooking.\n"
                "If asked about unrelated topics, politely decline and redirect the user back to cooking-related queries.\n"
                "Be concise, helpful, and ask clarifying questions when necessary.\n\n"
                # --- GENERALIZED FORMATTING RULE ---
                "**IMPORTANT FORMATTING RULE:**\n"
                "When a user's request (e.g., asking for a recipe suggestion, help with substitutes) requires you to ask multiple clarifying questions before you can provide a full answer, "
                "you MUST format these questions as a numbered list.\n"
                "Follow these specific formatting rules strictly:\n"
                "1. Start each numbered question on a new line.\n"
                "2. Separate each numbered question from the next with a blank line (use '\\n\\n').\n"
                "3. Do NOT use any markdown bolding (like **keyword**).\n"
                "4. Use a simple colon ':' after the keyword or introductory phrase for each question.\n\n"
                "**Example of the required format when asking clarifying questions:**\n"
                "Okay, I can help with [User's Request Goal]! To give you the best answer, please tell me:\\n\\n" # Note \\n\\n
                "1. Keyword1: [First question text]?\\n\\n" # Note \\n\\n
                "2. Keyword2: [Second question text]?\\n\\n" # Note \\n\\n
                "3. Keyword3: [Third question text]?"
                # --- END FORMATTING RULE ---
            )
            system_instruction = {"role": "system", "parts": [system_instruction_text]}

            # Initialize the model WITH the system instruction
            gemini_model = genai.GenerativeModel(
                model_name,
                system_instruction=system_instruction
            )
            logger.info(f"Google Generative AI configured successfully for model '{model_name}' with generalized formatting instructions.")

        except Exception as e:
            logger.error(f"Error configuring Google Generative AI: {e}", exc_info=True)
            gemini_model = None

# --- handle_chat_message function remains the same as the previous version ---
# It relies on the system instruction set during model initialization to guide formatting.
def handle_chat_message(user_id: str, message: str, session_key: str = None, chat_history: list = None) -> str:
    """
    Handles a user message using the Google Gemini API (configured with system instructions)
    and returns a response. Requires chat_history (managed via Django sessions
    in Gemini format) for context.
    """
    if gemini_model is None:
        logger.warning("Google Generative AI model not available. Using basic fallback response.")
        if "hello" in message.lower() or "hi" in message.lower():
            return "Hello! How can I help with recipes today?"
        return "Sorry, the AI assistant is currently unavailable. I can only offer limited help."

    if chat_history is None:
        chat_history = [] # Expecting Gemini format: [{'role': 'user'/'model', 'parts': ['text']}, ...]

    try:
        # Start chat session using history (model has system instructions)
        chat_session = gemini_model.start_chat(history=chat_history)
    except Exception as e:
         logger.error(f"Error starting Gemini chat session (check history format?): {e}", exc_info=True)
         return "Sorry, there was an issue starting the chat session."

    # Define generation configuration
    generation_config = genai.types.GenerationConfig(
        max_output_tokens=350,
        temperature=0.7,
    )

    # --- Call the Gemini API ---
    try:
        logger.debug(f"Sending to Gemini API (user_id={user_id}): '{message}' with history length {len(chat_history)}")
        response = chat_session.send_message(
            message,
            generation_config=generation_config,
        )

        if not response.parts:
             logger.warning(f"Gemini response had no parts for message: {message}")
             response_text = "Sorry, I didn't get a valid response. Could you try rephrasing?"
        else:
             # Check for safety ratings / blocked content if needed
             # if response.prompt_feedback.block_reason:
             #     logger.warning(f"Gemini request blocked. Reason: {response.prompt_feedback.block_reason}")
             #     return "I cannot respond to that request due to safety guidelines."
             # if not response.candidates[0].content.parts: # Check if candidate content is blocked
             #     logger.warning(f"Gemini response candidate blocked. Finish Reason: {response.candidates[0].finish_reason}, Safety: {response.candidates[0].safety_ratings}")
             #     return "My response was blocked due to safety guidelines."

             response_text = response.text # .text conveniently joins parts
        logger.debug(f"Received from Gemini API: {response_text}")
        return response_text

    # --- Handle Specific Google API Errors ---
    except google_exceptions.ResourceExhausted as e:
        logger.error(f"Google API Rate Limit Error: {e}", exc_info=True)
        return "The AI assistant is very popular right now! Please try again in a moment."
    except google_exceptions.PermissionDenied as e:
        logger.error(f"Google API Permission/Authentication Error: {e}", exc_info=True)
        return "Sorry, there seems to be an issue connecting to the AI assistant (authentication error)."
    except google_exceptions.InvalidArgument as e:
         logger.error(f"Google API Invalid Argument Error (check model/parameters): {e}", exc_info=True)
         return "Sorry, there was an issue sending the request to the AI assistant (invalid argument)."
    # --- Handle Generic Errors ---
    except Exception as e:
        logger.error(f"Unexpected error during Google API call: {e}", exc_info=True)
        return "Oops! Something unexpected went wrong while contacting the AI assistant. Please try again."