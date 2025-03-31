import os
import logging # Import logging
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages # Import Django messages framework
from .services import chatbot
from .forms import IngredientListForm, ImageUploadForm, ChatForm
from .services import ingredient_matcher, recommender, image_recognizer, chatbot # Import your service functions

# --- Logger Setup (Optional but Recommended) ---
logger = logging.getLogger(__name__)

# --- View for Feature 1: Suggest by Ingredients (Form based) ---
def suggest_recipes_view(request):
    suggestions = None
    form = IngredientListForm() # Initialize form for GET request

    if request.method == 'POST':
        form = IngredientListForm(request.POST)
        if form.is_valid():
            ingredients_str = form.cleaned_data['ingredients']
            # More robust parsing: handles spaces, multiple commas, newlines, filters empty strings
            ingredients_list = [
                ing.strip() for item in ingredients_str.split(',') # Initial split by comma
                for ing in item.split() # Split items by space/newline just in case
                if ing.strip() # Ensure it's not empty after stripping
            ]
            # Remove duplicates while preserving order (for Python 3.7+)
            ingredients_list = list(dict.fromkeys(ingredients_list))

            if ingredients_list:
                try:
                    suggestions = ingredient_matcher.suggest_recipes_by_ingredients(ingredients_list)
                    if not suggestions:
                         messages.info(request, "No recipes found matching those specific ingredients.")
                    # Optional: Add a success message if suggestions found
                    # else:
                    #    messages.success(request, f"Found {len(suggestions)} suggestions!")
                except Exception as e:
                    logger.error(f"Error suggesting recipes for {ingredients_list}: {e}", exc_info=True)
                    messages.error(request, "Sorry, an error occurred while trying to find suggestions.")
            else:
                messages.warning(request, "Please enter at least one ingredient.")
        # No need for else here, form errors will be displayed automatically

    context = {
        'form': form,
        'suggestions': suggestions,
    }
    return render(request, 'ai_module/suggest_recipes.html', context)

# --- View for Feature 2: Personalized Recommendations ---
@login_required # Ensures user is logged in
def personalized_recommendations_view(request):
    recommendations = None # Initialize
    try:
        # The recommender service function should accept the request.user object
        recommendations = recommender.get_personalized_recommendations(request.user)
        if not recommendations:
            messages.info(request, "We don't have personalized recommendations for you yet. Try rating some recipes!")
    except Exception as e:
        logger.error(f"Error getting recommendations for user {request.user.id}: {e}", exc_info=True)
        messages.error(request, "Sorry, an error occurred while fetching your recommendations.")

    context = {
        'recommendations': recommendations,
    }
    return render(request, 'ai_module/recommendations.html', context)

# --- View for Feature 3: Identify Ingredients from Image ---
def identify_ingredients_view(request):
    identified_ingredients = None # Initialize as None
    form = ImageUploadForm()

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            fs = None
            filename = None
            image_path = None
            suggestions = None # Initialize suggestions if you plan to use them

            try:
                # --- File Saving ---
                # Ensure MEDIA_ROOT is configured or handle appropriately
                if not settings.MEDIA_ROOT:
                     logger.error("MEDIA_ROOT setting is not configured. Cannot save uploaded image.")
                     messages.error(request, "Server configuration error: Cannot process image uploads.")
                     # Skip further processing if we can't save the file
                     # Return here or set a flag to prevent service call
                     # For simplicity, we'll let it proceed but log error later if path is None

                # Using FileSystemStorage explicitly:
                storage_location = os.path.join(settings.MEDIA_ROOT or '', 'ingredient_images')
                # Check if storage_location is valid before creating dirs/storage
                if storage_location:
                     os.makedirs(storage_location, exist_ok=True) # Ensure directory exists
                     fs = FileSystemStorage(location=storage_location)
                     filename = fs.save(image_file.name, image_file) # This might raise errors too
                     image_path = fs.path(filename)
                     logger.info(f"Image saved temporarily to: {image_path}")
                else:
                     # Handle case where MEDIA_ROOT wasn't set and we decided not to proceed
                      raise ValueError("Image storage location could not be determined.")


                # --- Call the image recognition service ---
                # Ensure image_path is valid before calling
                if image_path:
                    identified_ingredients = image_recognizer.identify_ingredients_from_image(image_path)
                else:
                    # Should not happen if ValueError was raised, but as fallback
                    logger.error("Image path was not set, skipping ingredient identification.")
                    messages.error(request, "Could not save the image for analysis.")
                    identified_ingredients = None # Explicitly set to None

                # --- Handle Service Results ---
                if identified_ingredients is None:
                    # Service indicated an error occurred (logged within the service)
                    messages.error(request, "Failed to analyze the image. Please check the image format or try again later.")
                    # identified_ingredients is already None for the context
                elif not identified_ingredients: # It's an empty list []
                    # Service worked, model found no ingredients
                    messages.warning(request, "Could not identify specific food ingredients in the photo. Try a clearer picture?")
                    # identified_ingredients is already [] for the context
                else: # It's a non-empty list
                    # Success!
                    ingredient_list_str = ", ".join(identified_ingredients)
                    messages.success(request, f"Identified: {ingredient_list_str}")
                    # identified_ingredients holds the list for the context

                    # --- Optional: Suggest recipes based on identified ingredients ---
                    # try:
                    #     suggestions = ingredient_matcher.suggest_recipes_by_ingredients(identified_ingredients)
                    #     # Add suggestions to context below if needed
                    #     if suggestions:
                    #          messages.info(request, "Found potential recipes based on identified ingredients.")
                    # except Exception as e_suggest:
                    #     logger.error(f"Error suggesting recipes after image ID {filename}: {e_suggest}")
                    #     messages.warning(request, "Identified ingredients, but couldn't fetch recipe suggestions right now.")
                    # --- End Optional Suggestions ---


            # --- Handle Specific Errors (File System / Other) ---
            except (OSError, IOError, ValueError, TypeError) as e: # Catch file system, value, type errors
                logger.error(f"Error processing image upload {getattr(image_file, 'name', 'N/A')}: {e}", exc_info=True)
                messages.error(request, f"An error occurred processing the uploaded file: {e}")
                identified_ingredients = None # Ensure it's None on error
            except Exception as e: # Catch-all for truly unexpected issues in the view
                logger.error(f"Unexpected error in identify_ingredients_view {filename or getattr(image_file, 'name', 'N/A')}: {e}", exc_info=True)
                messages.error(request, "An unexpected internal error occurred.")
                identified_ingredients = None # Ensure it's None on error
            finally:
                # --- File Cleanup ---
                # Delete the uploaded file if it exists and was saved
                if fs and filename and image_path and fs.exists(filename): # Check image_path too
                    try:
                        fs.delete(filename)
                        logger.info(f"Deleted temporary image file: {filename}")
                    except Exception as e_del:
                        # Log deletion error but don't necessarily show to user
                        logger.error(f"Error deleting temporary image file {filename}: {e_del}", exc_info=True)
        else:
             # Form is invalid
             messages.error(request, "Invalid submission. Please check the form below.")
             # identified_ingredients remains None

    # Prepare context for template rendering
    context = {
        'form': form,
        'identified_ingredients': identified_ingredients, # Will be None, [], or list[str]
        # 'suggestions': suggestions # Uncomment if adding suggestions
    }
    return render(request, 'ai_module/identify_ingredients.html', context)

# --- View for Feature 4: Chatbot API ---
@require_POST # This endpoint only accepts POST requests
@login_required(login_url=settings.LOGIN_URL) # Optional: Force login for API too, redirects handled by JS/frontend
def chatbot_api_view(request):
    try:
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
        except json.JSONDecodeError:
            logger.warning("Chatbot API received invalid JSON payload.")
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        if not message:
            logger.warning("Chatbot API received empty message.")
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        # --- Manage Chat History using Sessions (Gemini Format) ---
        # Retrieve history (ensure it's stored in Gemini format)
        chat_history_gemini_format = request.session.get('chat_history_gemini', [])

        # --- Call the AI Chatbot Service ---
        user_id = request.user.id if request.user.is_authenticated else None
        session_key = request.session.session_key

        # Pass the history in the format the service expects (now Gemini format)
        response_text = chatbot.handle_chat_message(
            user_id=user_id,
            message=message,
            session_key=session_key,
            chat_history=chat_history_gemini_format
        )

        # --- Update History in Session (Gemini Format) ---
        # Add user message
        chat_history_gemini_format.append({'role': 'user', 'parts': [message]})
        # Add model response
        chat_history_gemini_format.append({'role': 'model', 'parts': [response_text]})

        # Limit history length
        max_history_items = 10 # Store last 5 user/model turns
        request.session['chat_history_gemini'] = chat_history_gemini_format[-max_history_items:]
        request.session.modified = True # Ensure session is saved

        # --- Return Response ---
        return JsonResponse({'response': response_text})

    except Exception as e:
        logger.error(f"Chatbot API view error: {e}", exc_info=True)
        return JsonResponse({'error': 'An internal error occurred in the chat service.'}, status=500)


# --- DEPRECATED? View for Feature 4: Chatbot Interface Page ---
# This view might be unnecessary if the chat widget is always loaded via base.html
# Keep it if you have a dedicated full-page chat interface.
# Consider adding @login_required if only logged-in users can access this page.
# @login_required
def chat_interface_view(request):
    # form = ChatForm() # Form instance isn't strictly needed if handled by JS widget
    logger.info("Accessing dedicated chat interface view (confirm if needed).")
    # If this page IS used, ensure the template has the necessary HTML structure
    # for the chat widget JS in base.html to find its elements.
    return render(request, 'ai_module/chat_interface.html') # Pass context if needed {'form': form}