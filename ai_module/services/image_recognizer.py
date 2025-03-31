# ai_module/services/image_recognizer.py
import logging
import os
from django.conf import settings
from pathlib import Path # Use pathlib for better path handling
import mimetypes # To help guess image type

# --- Import the Google Generative AI library ---
try:
    import google.generativeai as genai
    # Import specific exceptions for better handling
    from google.api_core import exceptions as google_exceptions
    google_ai_available = True
except ImportError:
    genai = None
    google_exceptions = None
    google_ai_available = False
    # Log warning at module level
    logging.warning("Google Generative AI library not found. Image recognition disabled. Install with 'pip install google-generativeai'")

logger = logging.getLogger(__name__)

# --- Configure Google AI Client and Model ---
# This section attempts to configure the client and model once when the module is loaded.
gemini_vision_model = None
if google_ai_available:
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        logger.error("GOOGLE_API_KEY not found in Django settings. Gemini Vision features disabled.")
    else:
        try:
            genai.configure(api_key=api_key)
            # --- Choose a Gemini model capable of vision ---
            # Options: 'gemini-pro-vision', 'gemini-1.5-flash', 'gemini-1.5-pro'
            # 'gemini-1.5-flash' is often a good balance of capability and speed/cost.
            model_name = 'gemini-1.5-flash'
            gemini_vision_model = genai.GenerativeModel(model_name)
            # Test configuration with a simple check (optional)
            # gemini_vision_model.generate_content("test", generation_config=genai.types.GenerationConfig(max_output_tokens=5))
            logger.info(f"Google Generative AI Vision configured successfully for model '{model_name}'.")
        except Exception as config_error:
            logger.error(f"Error configuring Google Generative AI for Vision: {config_error}", exc_info=True)
            gemini_vision_model = None # Ensure model is None if configuration fails

def identify_ingredients_from_image(image_path: str) -> list[str] | None:
    """
    Identifies ingredients in an image using the Google Gemini Vision API.

    Args:
        image_path: The absolute path to the image file on the server.

    Returns:
        A list of identified ingredient names (strings), or None if an error occurs
        or the model/API is unavailable. Returns an empty list if the model
        responds with 'NONE'.
    """
    if gemini_vision_model is None:
        logger.error("Gemini Vision model is not available or not configured correctly.")
        # Optionally, you could raise an exception here instead of returning None
        # raise RuntimeError("Gemini Vision model not configured")
        return None # Indicate failure

    try:
        image_path_obj = Path(image_path)
        if not image_path_obj.is_file():
            logger.error(f"Image file not found or is not a file: {image_path}")
            return None

        logger.info(f"Processing image for ingredient identification: {image_path}")

        # --- Prepare the Image Input ---
        # Guess the MIME type
        mime_type, _ = mimetypes.guess_type(image_path_obj)
        if not mime_type or not mime_type.startswith('image/'):
            # Default or raise error if type cannot be determined or is not image
            mime_type = 'image/jpeg' # Default to JPEG if unsure
            logger.warning(f"Could not determine image MIME type for {image_path}, defaulting to {mime_type}")
            # Alternatively:
            # logger.error(f"Cannot determine valid image MIME type for {image_path}")
            # return None

        try:
            image_bytes = image_path_obj.read_bytes()
            image_part = {
                'mime_type': mime_type,
                'data': image_bytes
            }
        except (IOError, OSError) as file_err:
            logger.error(f"Error reading image file {image_path}: {file_err}", exc_info=True)
            return None

        # --- Create the Prompt ---
        # Be very specific about the desired output format.
        prompt_text = (
            "Carefully examine the provided image. Identify only the distinct food ingredients visible. "
            "List the names of the ingredients separated by commas (e.g., 'tomato, onion, garlic'). "
            "Be specific where possible (e.g., 'red bell pepper' instead of just 'bell pepper'). "
            "Do not include quantities, descriptions, non-food items, or any explanatory text. "
            "If no food ingredients are clearly identifiable, respond ONLY with the word 'NONE'."
        )
        prompt_parts = [image_part, prompt_text] # Order matters: image often comes first

        # --- Define Generation Configuration ---
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,      # Low temperature for more factual, less creative output
            max_output_tokens=200,# Limit length, should be enough for ingredient list
            # top_p=0.95,         # Alternative sampling method
            # top_k=40            # Alternative sampling method
        )

        # --- Call the Gemini Vision API ---
        logger.debug(f"Sending request to Gemini Vision model '{gemini_vision_model.model_name}'...")
        response = gemini_vision_model.generate_content(
            prompt_parts,
            generation_config=generation_config,
            request_options={'timeout': 45} # Add a timeout (in seconds)
        )

        # --- Process the Response ---
        # Access the text response safely
        response_text = response.text.strip()
        logger.debug(f"Received raw response from Gemini Vision: '{response_text}'")

        if not response_text:
             logger.warning(f"Gemini Vision returned an empty response for image: {image_path}")
             return [] # Treat empty response as no ingredients found

        # Check for the specific "NONE" response
        if response_text.upper() == 'NONE':
            logger.info(f"Gemini Vision identified no ingredients in image: {image_path}")
            return [] # Return empty list if model explicitly says none

        # Parse the comma-separated list
        ingredients = [ing.strip().lower() for ing in response_text.split(',') if ing.strip()]
        # Remove potential duplicates while preserving order (Python 3.7+)
        ingredients = list(dict.fromkeys(ingredients))

        logger.info(f"Identified ingredients for {image_path}: {ingredients}")
        return ingredients

    # --- Handle Specific Google API Errors ---
    except google_exceptions.ResourceExhausted as e:
        logger.error(f"Google API Rate Limit Error processing image {image_path}: {e}", exc_info=True)
        # Consider re-raising a custom exception or returning a specific marker
        return None # Indicate failure due to rate limit
    except google_exceptions.PermissionDenied as e:
        logger.error(f"Google API Permission/Authentication Error processing image {image_path}: {e}", exc_info=True)
        return None # Indicate failure due to auth issue
    except google_exceptions.InvalidArgument as e:
         logger.error(f"Google API Invalid Argument Error processing image {image_path} (check model/parameters/image format): {e}", exc_info=True)
         return None # Indicate failure due to bad request args
    except google_exceptions.GoogleAPICallError as e:
         # Catch other Google API call errors (network issues, etc.)
         logger.error(f"Google API Call Error processing image {image_path}: {e}", exc_info=True)
         return None
    # --- Handle Generic Errors ---
    except Exception as e:
        logger.error(f"Unexpected error identifying ingredients in image {image_path}: {e}", exc_info=True)
        return None # Indicate generic failure