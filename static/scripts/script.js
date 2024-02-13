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
