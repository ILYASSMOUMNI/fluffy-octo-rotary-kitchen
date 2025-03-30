# ai_module/services/image_recognizer.py
import os
import random # Optional: to return slightly varied dummy data

# Remove imports related to requests, base64, and settings if they are no longer needed anywhere else in this file.
# from django.conf import settings # No longer needed for API key

# --- Placeholder Image Recognition ---

def identify_ingredients_from_image(image_path: str) -> list[str]:
    """
    Placeholder function for identifying ingredients from an image.
    Does NOT actually process the image or use external APIs.

    Args:
        image_path: The path to the image file (received but not used).

    Returns:
        A predefined list of ingredients or an empty list for testing purposes.
    """
    print(f"--- Placeholder Image Recognition ---")
    print(f"Received image path: {image_path}")
    print("NOTE: Image is NOT being processed. Returning dummy data.")

    # Example: Return a fixed list
    # return ["tomato", "onion", "garlic", "bell pepper"]

    # Example: Return a randomly selected list for variety during testing
    possible_ingredients = [
        ["apple", "banana", "orange"],
        ["chicken breast", "broccoli", "rice"],
        ["pasta", "tomato sauce", "parmesan cheese"],
        ["flour", "sugar", "eggs", "butter"],
        [], # Sometimes return empty
    ]
    dummy_result = random.choice(possible_ingredients)

    # Optional: You might still want to check if the file exists, even if not processing it
    if not os.path.exists(image_path):
        print(f"Warning: Image file not found at {image_path}, but returning dummy data anyway.")
        # You could choose to return [] here if the file doesn't exist
        # return []

    print(f"Returning dummy ingredients: {dummy_result}")
    return dummy_result

    # If you want it to always return empty, just use:
    # return []