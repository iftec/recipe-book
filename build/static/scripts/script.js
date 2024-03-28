async function makeFetchRequest(url, method, data, successMessage, errorMessage) {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const responseData = await response.json();

        if (responseData.success) {
            if (successMessage) {
                showNotification(successMessage, true);
            }
            return responseData;
        } else {
            throw new Error(responseData.message || 'Request failed.');
        }
    } catch (error) {
        if (errorMessage) {
            showNotification(errorMessage, false);
        }
        return { success: false, message: 'An error occurred.' };
    }
}

function toggleMenu() {
    const menu = document.querySelector('.menu');

    if (menu.style.width === '100%') {
        menu.style.width = '0'; // Close the menu
    } else {
        menu.style.width = '100%'; // Open the menu
    }
}

async function addToFavorites(recipeId) {
    const url = `/add_to_favorites/${recipeId}`;
    const method = 'POST';
    const data = {};
    const successMessage = 'Recipe added to favorites!';
    const errorMessage = 'This recipe is already your favorites!!';

    const responseData = await makeFetchRequest(url, method, data, successMessage, errorMessage);

    if (responseData.success) {
        // Redirect to a new page or perform other actions after successful addition to favorites
        window.location.href = '/favorites';  // Redirect to the favorites page
    } else {
        // Display an error message if adding to favorites failed
        alert(responseData.message);
    }
}

function printPageArea(recipeID) {
    var printContent = document.getElementById('printableArea' + recipeID).innerHTML;
    var originalContent = document.body.innerHTML;
    document.body.innerHTML = printContent;
    window.print();
    document.body.innerHTML = originalContent;
}

async function removeFromFavorites(recipeId) {
    const confirmation = confirm('Are you sure you want to remove this recipe from favorites?');

    if (confirmation) {
        try {
            const response = await fetch('/remove_from_favorites/' + recipeId, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ recipe_id: recipeId })
            });

            const data = await response.json();

            if (data.success) {
                var favoriteElement = document.getElementById('favorite-' + recipeId);
                if (favoriteElement) {
                    favoriteElement.remove();
                }
            } else {
                showNotification('Failed to remove recipe from favorites.', false);
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('An error occurred while removing recipe from favorites.', false);
        }
    }
}


function showNotification(message, isSuccess) {
    alertMsg = isSuccess ? 'Success: ' + message : 'Sorry: ' + message;
    alert(alertMsg);
}

async function addRecipe(formData) {
    try {
        const response = await fetch('/add_recipe', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Recipe added successfully, redirect to the specified URL
            alert(data.message);
            window.location.href = data.redirect_url;
        } else {
            // Display an alert message if there was an error adding the recipe
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while adding the recipe.');
    }
}

async function confirmDelete(recipeId) {
    if (confirm("Are you sure you want to delete this recipe?")) {

        try {
            const response = await fetch('/delete_recipe/' + recipeId, {
            method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                alert(data.message); // Display success message
                window.location.href = data.redirect_url; // Redirect to the specified URL
            } else {
                alert(data.message); // Display error message
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while deleting the recipe.');
        }
    }
}

document.getElementById('addRecipeForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    const formData = new FormData(this); // Create FormData object from the form

    // Call the addRecipe function with the form data
    addRecipe(formData);
});

document.addEventListener('DOMContentLoaded', function () {
    const toggler = document.querySelector('.toggler');
    toggler.addEventListener('change', toggleMenu);
});

module.exports = {
    makeFetchRequest,
    addToFavorites,
    // other functions
  };