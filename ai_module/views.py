import os
import logging # Import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages # Import Django messages framework

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
    # Uses Django Messages Framework instead of explicit error_message context
    identified_ingredients = None
    form = ImageUploadForm() # Initialize for GET

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            fs = None
            filename = None
            image_path = None

            # Define storage location robustly - use default storage if MEDIA_ROOT is not set
            # Or better: Use Django's default_storage if suitable
            # from django.core.files.storage import default_storage
            # filename = default_storage.save(f'ingredient_images/{image_file.name}', image_file)
            # image_path = default_storage.path(filename)

            # Using FileSystemStorage explicitly:
            try:
                if not settings.MEDIA_ROOT:
                     logger.warning("MEDIA_ROOT setting is not configured. Files may not be saved correctly.")
                     # Consider falling back to a temporary directory or raising an error
                     # raise ImproperlyConfigured("MEDIA_ROOT is not set.") # Or handle differently

                storage_location = os.path.join(settings.MEDIA_ROOT or '', 'ingredient_images')
                os.makedirs(storage_location, exist_ok=True) # Ensure directory exists
                fs = FileSystemStorage(location=storage_location)
                filename = fs.save(image_file.name, image_file)
                image_path = fs.path(filename)

                # Call the image recognition service
                identified_ingredients = image_recognizer.identify_ingredients_from_image(image_path)

                if not identified_ingredients:
                    messages.warning(request, "Could not identify specific ingredients. Try a clearer photo?")
                else:
                    messages.success(request, "Successfully identified ingredients!")
                    # Optional: Suggest recipes immediately (could make the response slower)
                    # try:
                    #     suggestions = ingredient_matcher.suggest_recipes_by_ingredients(identified_ingredients)
                    #     context['suggestions'] = suggestions # Need to add 'suggestions' to context below
                    # except Exception as e_suggest:
                    #     logger.error(f"Error suggesting recipes after image ID {filename}: {e_suggest}")
                    #     messages.info(request, "Identified ingredients, but couldn't fetch recipe suggestions right now.")


            except (OSError, IOError) as e: # More specific file system errors
                logger.error(f"File system error processing image {getattr(image_file, 'name', 'N/A')}: {e}", exc_info=True)
                messages.error(request, f"A file system error occurred: {e}")
            except Exception as e: # Catch-all for service errors or unexpected issues
                logger.error(f"Error processing image {filename or getattr(image_file, 'name', 'N/A')}: {e}", exc_info=True)
                messages.error(request, "An unexpected error occurred while processing the image.")
            finally:
                # --- File Cleanup ---
                # Delete the uploaded file if it exists and was saved, as it's likely temporary
                if fs and filename and fs.exists(filename):
                    try:
                        fs.delete(filename)
                        logger.info(f"Deleted temporary image file: {filename}")
                    except Exception as e_del:
                        logger.error(f"Error deleting temporary image file {filename}: {e_del}", exc_info=True)
        # No else needed for form invalid, errors handled by form rendering

    context = {
        'form': form,
        'identified_ingredients': identified_ingredients,
        # 'suggestions': suggestions # Add if generating suggestions too
    }
    # Make sure your template iterates through {% messages %} tag:
    # {% if messages %}
    #   <ul class="messages">
    #     {% for message in messages %}
    #       <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
    #     {% endfor %}
    #   </ul>
    # {% endif %}
    return render(request, 'ai_module/identify_ingredients.html', context)

# --- View for Feature 4: Chatbot API ---
@require_POST # This endpoint only accepts POST requests
@login_required(login_url=settings.LOGIN_URL) # Optional: Force login for API too, redirects handled by JS/frontend
def chatbot_api_view(request):
    # Consider checking request.headers.get('x-requested-with') == 'XMLHttpRequest' for AJAX
    if not request.is_ajax() and not 'application/json' in request.META.get('HTTP_ACCEPT', ''):
         # Return error if not an AJAX or API-like request
         return JsonResponse({'error': 'Invalid request type'}, status=400)

    try:
        # Directly parse JSON body instead of relying on form for APIs
        import json
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        if not message:
             return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        user_id = request.user.id if request.user.is_authenticated else None # Use ID or None
        session_key = request.session.session_key # Good identifier for anonymous or stateful chats

        # Get response from the chatbot service function
        response_text = chatbot.handle_chat_message(user_id=user_id, message=message, session_key=session_key) # Pass necessary identifiers

        return JsonResponse({'response': response_text})

    except Exception as e:
        logger.error(f"Chatbot API error for user {request.user.id if request.user.is_authenticated else 'anonymous'}: {e}", exc_info=True)
        # Don't expose detailed errors in production API responses
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