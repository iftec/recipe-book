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


function submitSearchForm() {
    document.getElementById('searchForm').submit();
}

async function addToFavorites(recipeId) {
    const url = `/add_to_favorites/${recipeId}`;
    const method = 'POST';
    const data = {};
    const successMessage = 'Recipe added to favorites!';
    const errorMessage = 'This recipe is already in your favorites!!';

    const responseData = await makeFetchRequest(url, method, data, successMessage, errorMessage);

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
                
                // Refresh the page after successful removal
                location.reload();
            } else {
                showNotification('Failed to remove recipe from favorites.', false);
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('An error occurred while removing recipe from favorites.', false);
        }
    }

    isRemoving = false; // Reset the flag after removal is complete
}

function showNotification(message, isSuccess) {
    if (isSuccess) {
        alert('Success: ' + message);
    } else {
        alert('Sorry: ' + message);
    }
}

function confirmDelete(recipeId) {
    if (confirm("Are you sure you want to delete this recipe?")) {
        // If user confirms, submit the form
        document.getElementById('deleteForm' + recipeId).submit();
    } else {
        // If user cancels, do nothing
        return false;
    }
}