document.addEventListener("DOMContentLoaded", function() {
    setupTimesEatenButtons();
    setupDeleteButtons();
    setupStarRating();
    setupComment();
    setupIsFavorite();
    setupFavoriteDish();
    setupRestaurantDetailButtons();
});

function setupTimesEatenButtons() {
    // Get increment button and attach click event listeners
    let incrementButtons = document.querySelectorAll('.increment');
    incrementButtons.forEach(button => {
        button.addEventListener('click', function() {
            let dataId = this.getAttribute('data-id');
            updateTimesEaten(dataId, 1);
        });
    });

    // Get  decrement button and attach click event listeners
    let decrementButtons = document.querySelectorAll('.decrement');
    decrementButtons.forEach(button => {
        button.addEventListener('click', function() {
            let dataId = this.getAttribute('data-id');
            updateTimesEaten(dataId, -1);
        });
    });
}

function setupStarRating() {
    document.querySelectorAll('.star-rating').forEach(ratingContainer => {
        let rating = parseFloat(ratingContainer.getAttribute('data-rating'));
        let stars = ratingContainer.querySelectorAll('i');

        stars.forEach((star, index) => {
            let starValue = index + 1;
            
            if (starValue <= rating) {
                star.className = "bi bi-star-fill active";
            } else if (starValue - 0.5 === rating) {
                star.className = "bi bi-star-half active";
            } else {
                star.className = "bi bi-star";
            }
        });

        ratingContainer.querySelectorAll('i').forEach(star => {
            star.addEventListener('click', function(e) {
                let rect = e.currentTarget.getBoundingClientRect();
                let clickPositionX = e.clientX - rect.left;
                let isHalfStar = (clickPositionX < rect.width / 1.6);
                
                let value = parseInt(e.currentTarget.getAttribute('data-value'));
                if (isHalfStar) value -= 0.5;
    
                // Update the stars visually within the current row/container
                ratingContainer.querySelectorAll('i').forEach((s, index) => {
                    let starValue = parseInt(s.getAttribute('data-value'));
                    if (starValue <= value) {
                        s.className = "bi bi-star-fill active"; // full star
                    } else if (starValue - 0.5 === value) {
                        s.className = "bi bi-star-half active"; // half star
                    } else {
                        s.className = "bi bi-star"; // empty star
                    }
                });

                let inputField = ratingContainer.closest('tr').querySelector('input[name="user_rating"]');
                if (inputField) {
                    inputField.value = value;
                    console.log(value);
                    updateRating(inputField.getAttribute('data-id'), value);
                }
            });
        });
    });
    
}

function updateTimesEaten(dataId, change) {
    let formData = new FormData();
    formData.append('change', change);

    fetch(`/update_times_eaten/${dataId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the times eaten span
            let timesEatenSpan = document.querySelector(`#times-eaten-${dataId}`);
            timesEatenSpan.innerText = (parseInt(timesEatenSpan.innerText) + change).toString();
        } else {
            alert('Error updating times eaten');
        }
    });
}

function updateRating(dataId, rating) {
    let formData = new FormData();
    formData.append('rating', rating);

    fetch(`/update_rating/${dataId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // location.reload();  // Refresh the page to see the updated value
        } else {
            alert('Error updating times eaten');
        }
    });
}

function setupComment() {
    const commentTextareas = document.querySelectorAll('.user-comment')

    commentTextareas.forEach(textarea => {
        textarea.addEventListener('change', function(e) {
            const textareaElement = e.currentTarget;
            const dataId = textarea.getAttribute('data-id');

            let formData = new FormData();
            const comment = textareaElement.value;
            formData.append('comment', comment);

            fetch(`/update_comment/${dataId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // location.reload();  // Refresh the page to see the updated value
                } else {
                    alert('Error updating times eaten');
                }
            });
        });
    });
}

function setupIsFavorite() {
    const isFavoriteButtons = document.querySelectorAll('.is-favorite');
    isFavoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const buttonElement = e.currentTarget;
            const dataId = button.getAttribute('data-id');

            let formData = new FormData();
            const isFavorite = buttonElement.checked;
            console.log(typeof isFavorite);
            formData.append('is_favorite', isFavorite);

            fetch(`/update_is_favorite/${dataId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // location.reload();  // Refresh the page to see the updated value
                } else {
                    alert('Error updating times eaten');
                }
            });
        });
    });
}

function setupFavoriteDish() {
    const favoriteDishTextareas = document.querySelectorAll('.favorite-dish')

    favoriteDishTextareas.forEach(textarea => {
        textarea.addEventListener('change', function(e) {
            const textareaElement = e.currentTarget;
            const dataId = textarea.getAttribute('data-id');

            let formData = new FormData();
            const favoriteDish = textareaElement.value;
            console.log(favoriteDish);
            formData.append('favorite_dish', favoriteDish);

            fetch(`/update_favorite_dish/${dataId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // location.reload();  // Refresh the page to see the updated value
                } else {
                    alert('Error updating times eaten');
                }
            });
        });
    });
}

function setupDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-button');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            console.log(button)
            console.log(button.getAttribute('data-id'))
            const dataId = button.getAttribute('data-id');
            console.log(dataId);
            fetch(`/delete_user_restaurant/${dataId}/`, {
                method: 'POST',
                
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const row = button.closest('tr');
                    row.remove();
                } else {
                    alert('Error updating times eaten');
                }
            });
        });
    });
}

function setupRestaurantDetailButtons() {
    GOOGLE_API_KEY = "HIDDEN"
    const detailButtons = document.querySelectorAll('.btn-primary');

    detailButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const placeId = this.getAttribute('place-id');
            console.log(placeId);
            formData = new FormData();
            fetch(`/fetch_restaurant_details/${placeId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                
            })
            .then(response => response.json())
            .then(updateModal)
            .catch(error => console.error('Error fetching data:', error));
        });
    });
}

function updateModal(data) {
    const restaurantDetails = data.restaurantDetails;
    document.getElementById('restaurant-name').textContent = restaurantDetails.name;
    document.getElementById('restaurant-address').textContent = restaurantDetails.address;
    document.getElementById('restaurant-phone').textContent = restaurantDetails.phone_number;
    document.getElementById('restaurant-rating').textContent = restaurantDetails.rating + "/5";
    
    var websiteLink = document.getElementById('restaurant-website');
    websiteLink.href = restaurantDetails.website;
    websiteLink.textContent = restaurantDetails.website;

    // Badges
    document.getElementById('delivery-badge').style.display = restaurantDetails.delivery ? "inline" : "none";
    document.getElementById('pickup-badge').style.display = restaurantDetails.pickup ? "inline" : "none";
    document.getElementById('dinein-badge').style.display = restaurantDetails.dinein ? "inline" : "none";

    // Schedule
    console.log(restaurantDetails);
    var weekdaysContainer = document.getElementById('opening-hours');
    weekdaysContainer.innerHTML = '';
    for (var day of restaurantDetails.weekday_text) {
        var li = document.createElement('li');
        li.textContent = day;
        li.className = 'mb-2';
        weekdaysContainer.appendChild(li);
    }

    // Reviews
    var reviewsContainer = document.getElementById('reviews-container');
    reviewsContainer.innerHTML = '';

    restaurantDetails.reviews.forEach(function(review) {
        var reviewCard = createReviewCard(review);
        reviewsContainer.appendChild(reviewCard);
    });

    // Images
    var imagesContainer = document.getElementById('images-container');
    imagesContainer.innerHTML = '';
    restaurantDetails.photo_references.forEach(function(photo_ref) {
        var img = document.createElement('img');
        img.src = `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=${photo_ref}&key=${GOOGLE_API_KEY}`;
        img.alt = restaurantDetails.name;
        img.className = 'img-fluid mb-3';
        img.style.width = '49%';
        imagesContainer.appendChild(img);
    });

    const modalElement = document.getElementById('restaurantDetailsModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

function createReviewCard(review) {
    const reviewCard = document.createElement('div');
    reviewCard.className = 'card mb-2';
    reviewCard.style.maxWidth = '90%';
    reviewCard.style.width = '90%';
    reviewCard.style.margin = '0 auto';

    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';

    // Profile image
    if (review.profile_photo_url) {
        const profileImage = document.createElement('img');
        profileImage.src = review.profile_photo_url;
        profileImage.alt = review.author_name;
        profileImage.className = 'rounded-circle';
        profileImage.style.width = '50px';
        profileImage.style.height = '50px';
        cardBody.appendChild(profileImage);
    }

    // Author name
    const authorName = document.createElement('strong');
    authorName.textContent = review.author_name;
    cardBody.appendChild(authorName);

    // Rating stars
    const ratingDiv = document.createElement('div');
    ratingDiv.className = 'mt-2';
    for (let i = 1; i <= 5; i++) {
        const starIcon = document.createElement('i');
        if (i <= review.rating) {
            starIcon.className = 'bi bi-star-fill';
            starIcon.style.color = 'orange';
        } else {
            starIcon.className = 'bi bi-star-fill';
            starIcon.style.color = 'rgb(171, 171, 171)';
        }
        ratingDiv.appendChild(starIcon);
    }
    cardBody.appendChild(ratingDiv);

    // Review text
    var reviewText = document.createElement('p');
    reviewText.textContent = review.text;
    cardBody.appendChild(reviewText);

    // Review time
    if (review.time) {
        const reviewTime = document.createElement('small');
        reviewTime.className = 'text-muted';

        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        const date = new Date(review.time);

        reviewTime.textContent = date.toLocaleDateString(undefined, options);;

        cardBody.appendChild(reviewTime);
    }

    reviewCard.appendChild(cardBody);

    return reviewCard;
}


// For fetching the CSRF token. Found in Django docs
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
