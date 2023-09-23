import json
import requests
import geocoder
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from .models import *
from .forms import *
from .utils import *

GOOGLE_API_KEY = "HIDDEN"

def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'An error occurred')
    context= {'form':form}
    return render(request, 'core/register.html', context)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not match')
    return render(request, 'core/login.html')

def user_logout(request):
    # log the user out
    logout(request)
    return redirect('home')

def random_restaurant_finder(request):
    random_restaurant = {}
    g = geocoder.ip('me')
    latitude = g.latlng[0]
    longitude = g.latlng[1]
    user_location_coords = (latitude, longitude)
    nearby_restaurant_form = NearbyRestaurantSearchForm()
    number_of_results = -1
    
    # get saved restaurants of the user
    saved_restaurants = []
    saved_restaurants_place_ids = []
    if request.user.is_authenticated:
        saved_restaurants = UserRestaurantData.objects.filter(user=request.user)
        for saved_restaurant in saved_restaurants:
            saved_restaurants_place_ids.append(saved_restaurant.restaurant.place_id)
    
    if request.method == 'POST':
        nearby_restaurant_form = NearbyRestaurantSearchForm(request.POST)
        submitted_form = request.POST.get('form_type')
        
        if submitted_form == 'nearby_restaurant_form' and nearby_restaurant_form.is_valid():
            min_rating = nearby_restaurant_form.cleaned_data['min_rating']
            max_distance = nearby_restaurant_form.cleaned_data['max_distance']
            type = nearby_restaurant_form.cleaned_data['type']
            
            # Fetch the JSON data from the Google Places API
            json_data = fetch_json_data(f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={type}&location={latitude}%2C{longitude}&radius={max_distance * 1609.34}&type=restaurant&key={GOOGLE_API_KEY}")
            number_of_results = get_number_of_results(json_data)
            random_restaurant = extract_random_restaurant(json_data)
            
            # If the random restaurant is not within the rating range, find a new one, but don't repeat the same restaurant
            processed_ids = set()
            processed_ids.add(random_restaurant['place_id'])
            
            while random_restaurant['rating'] < min_rating and len(processed_ids) < number_of_results:
                random_restaurant = extract_random_restaurant(json_data)
                processed_ids.add(random_restaurant['place_id'])
                
            random_restaurant_location_coords = (random_restaurant['lat'], random_restaurant['lng'])
            random_restaurant['distance'] = get_distance_between(user_location_coords, random_restaurant_location_coords)
            random_restaurant['details'] = get_restaurant_details(random_restaurant['place_id'])
            
            # Makes the fields don't reset when submitting the form
            nearby_restaurant_form = NearbyRestaurantSearchForm(request.POST)
            
        elif submitted_form == 'save_restaurant':
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                restaurant = Restaurant(
                    name = request.POST['name'],
                    address = request.POST['address'],
                    place_id = request.POST['place_id']
                )
                restaurant.save()
                print('Saved successfully')
            except Exception as e:
                print('Error while saving:', e)
            
            try:  
                user_restaurant_data = UserRestaurantData(
                    user = request.user,
                    restaurant = restaurant,
                    
                )
                user_restaurant_data.save()
            except Exception as e:
                print('Error while saving:', e)
            
    context = {'range_1_to_5': range(1, 6),'restaurant': random_restaurant, 'nearby_restaurant_form': nearby_restaurant_form, 'saved_restaurants_place_ids': saved_restaurants_place_ids, 
               'number_of_results': number_of_results, 'GOOGLE_API_KEY': GOOGLE_API_KEY}
    return render(request, 'core/random_restaurant_finder.html', context)

def home(request):
    nearby_restaurants = []
    # get saved restaurants of the user
    saved_restaurants = []
    saved_restaurants_place_ids = []
    if request.user.is_authenticated:
        saved_restaurants = UserRestaurantData.objects.filter(user=request.user)
        for saved_restaurant in saved_restaurants:
            saved_restaurants_place_ids.append(saved_restaurant.restaurant.place_id)
    
    specific_restaurant = {}
    number_of_results = -1
    g = geocoder.ip('me')
    latitude = g.latlng[0]
    longitude = g.latlng[1]
    user_location_coords = (latitude, longitude)

    nearby_restaurant_form = {}
    specific_restaurant_form = {}
    if request.method == 'POST':
        nearby_restaurant_form = NearbyRestaurantSearchForm(request.POST)
        specific_restaurant_form = SpecificRestaurantSearchForm(request.POST)
        submitted_form = request.POST.get('form_type')
        
        if submitted_form == 'nearby_restaurants_form' and nearby_restaurant_form.is_valid():
            min_rating = nearby_restaurant_form.cleaned_data['min_rating']
            max_distance = nearby_restaurant_form.cleaned_data['max_distance']
            type = nearby_restaurant_form.cleaned_data['type']
            
            # Fetch the JSON data from the Google Places API
            json_data = fetch_json_data(f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={type}&location={latitude}%2C{longitude}&radius={max_distance * 1609.34}&type=restaurant&key={GOOGLE_API_KEY}")
            nearby_restaurants = get_all_restaurants(json_data)
            
            nearby_restaurants = get_filtered_restaurants_concurrently(nearby_restaurants, user_location_coords, min_rating)
            
            number_of_results = len(nearby_restaurants)
            
            # Makes the fields don't reset when submitting the form
            nearby_restaurant_form = NearbyRestaurantSearchForm(request.POST)

        elif submitted_form == 'specific_restaurant_form' and specific_restaurant_form.is_valid():
            name = specific_restaurant_form.cleaned_data['name']
            address = specific_restaurant_form.cleaned_data['address']
            keywords = specific_restaurant_form.cleaned_data['keywords']
            
            specific_restaurant = get_specific_restaurant(name, address, keywords)
            specific_restaurant_location_coords = (specific_restaurant['lat'], specific_restaurant['lng'])
            specific_restaurant['distance'] = get_distance_between(user_location_coords, specific_restaurant_location_coords)
            specific_restaurant['details'] = get_restaurant_details(specific_restaurant['place_id'])
            
            # Makes the fields don't reset when submitting the form
            specific_restaurant_form = SpecificRestaurantSearchForm(request.POST)
        elif submitted_form == 'save_restaurant':
            if not request.user.is_authenticated:
                return redirect('login')
            
            print(specific_restaurant)
            try:
                restaurant = Restaurant(
                    name = request.POST['name'],
                    address = request.POST['address'],
                    place_id = request.POST['place_id']
                )
                restaurant.save()
                print('Saved successfully')
            except Exception as e:
                print('Error while saving:', e)
            
            try:  
                user_restaurant_data = UserRestaurantData(
                    user = request.user,
                    restaurant = restaurant,
                    
                )
                user_restaurant_data.save()
            except Exception as e:
                print('Error while saving:', e)
                 
    
    context = {'nearby_restaurants':nearby_restaurants, 'range_1_to_5': range(1, 6), 'GOOGLE_API_KEY': GOOGLE_API_KEY, 'specific_restaurant_form': specific_restaurant_form,
               'specific_restaurant': specific_restaurant, 'number_of_results': number_of_results, 'saved_restaurants_place_ids': saved_restaurants_place_ids,}

    return render(request, 'core/home.html', context)

@login_required(login_url='login')
def dining_diary(request):
    user_restaurants = UserRestaurantData.objects.filter(user=request.user)
    context = {'user_restaurants': user_restaurants}
    return render(request, 'core/dining_diary.html', context)

def fetch_restaurant_details(request, place_id):
    return JsonResponse({'restaurantDetails': get_restaurant_details(place_id)})

def update_times_eaten(request, data_id):
    if request.method == "POST":
        change = int(request.POST.get('change', 0))
        data = UserRestaurantData.objects.get(id=data_id)
        data.times_eaten += change
        data.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

def update_rating(request, data_id):
    if request.method == "POST":
        rating = float(request.POST.get('rating', 0))
        data = UserRestaurantData.objects.get(id=data_id)
        data.user_rating = rating
        data.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

def update_comment(request, data_id):
    if request.method == "POST":
        comment = request.POST.get('comment', '')
        print(request.POST)
        print(comment)
        data = UserRestaurantData.objects.get(id=data_id)
        data.user_comment = comment
        data.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

def update_is_favorite(request, data_id):
    if request.method == "POST":
        is_favorite = request.POST.get('is_favorite', False).lower() == 'true'
        data = UserRestaurantData.objects.get(id=data_id)
        data.is_favorite = is_favorite
        data.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

def update_favorite_dish(request, data_id):
    if request.method == "POST":
        favorite_dish = request.POST.get('favorite_dish', '')
        print(request.POST)
        print(favorite_dish)
        print(data_id)
        data = UserRestaurantData.objects.get(id=data_id)
        data.favorite_dish = favorite_dish
        data.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})
    
def delete_user_restaurant(request, data_id):
    if request.method == "POST":
        data = UserRestaurantData.objects.get(id=data_id)
        data.delete()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})